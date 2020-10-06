import os
import sys
import time
import enum
import uuid
import pprint
import socket
import shutil
import logging
import requests
import tempfile
import threading
import traceback
import subprocess
import sentry_sdk
from sentry_sdk import utils
import collections
import multiprocessing
from typing import Dict, List, Callable
from abc import ABC, abstractmethod
from queue import Queue


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.utils import deprecated
from perceptilabs.issues import IssueHandler, UserlandError
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.utils import TracebackFrame
from perceptilabs.core_new.layers import TrainingSupervised, TrainingReinforce, TrainingRandom
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.communication import TrainingClient, State
from perceptilabs.script import ScriptFactory, FetchParameterError
from perceptilabs.core_new.communication.deployment import ThreadStrategy, DeploymentStrategy
from perceptilabs.messaging import MessagingFactory
from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER
import perceptilabs.dataevents as dataevents


logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)

# Train from a file named training_file.py and keep it in the temp directory unless we're in development mode
training_script_name = "training_script.py" if os.getenv("PL_DEV") else f"{tempfile.gettempdir()}/training_script.py"


class Core:
    def __init__(self, graph_builder: GraphBuilder, script_factory: ScriptFactory, messaging_factory: MessagingFactory, issue_handler: IssueHandler=None, running_mode = 'training', server_timeout=610, userland_timeout=600, deployment_strategy=None, use_sentry=False, samplers=None):
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._messaging_factory = messaging_factory
        self._graphs = collections.deque(maxlen=500)
        self._last_graph = None
        self._graph_spec = None
        self._issue_handler = issue_handler
        self._use_sentry = use_sentry
        self._samplers = samplers or []
        self._running_mode = running_mode
        self._deployment_strategy = deployment_strategy or ThreadStrategy()

        self._server_timeout = server_timeout
        self._userland_timeout = userland_timeout
        self._training_session_id = None

        self._client = None
        self._closed_by_server = False
        self._closed_by_force = False
        self._collected_start_metrics = False


        self._time_paused = 0
        self._paused_time_stamp = None
        self._time_started = None
        self._time_ended = None
        
    def run(self, graph_spec: GraphSpec, on_iterate: List[Callable]=None, auto_close=False, model_id: int=None):
        on_iterate = on_iterate or []
        self._graph_spec = graph_spec
        step = self.run_stepwise(graph_spec, auto_close=auto_close, model_id=model_id)
        for counter, _ in enumerate(step):
            if counter % 100 == 0:
                logger.debug(f"Running step {counter}")

            for f in on_iterate:
                f(counter, self)
        
    def run_stepwise(self, graph_spec, auto_close=False, model_id=None):
        self._training_session_id = training_session_id = uuid.uuid4().hex
        logger.info(f"Core.run_stepwise called. Training session: [{training_session_id}]")
        
        self._model_id = model_id or uuid.uuid4().int
        topic_generic = f'generic-{training_session_id}'.encode()    
        topic_snapshots = f'snapshots-{training_session_id}'.encode()
        producer = self._messaging_factory.make_producer(topic_generic)        
        consumer = self._messaging_factory.make_consumer([topic_generic, topic_snapshots])
        logger.info(f"Instantiated message producer/consumer pairs for topics {topic_generic} and {topic_snapshots} for training session {training_session_id}")
        
        #graph = self._graph_builder.build_from_spec(graph_spec)        
        script_path = self._create_script(graph_spec, training_session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)

        try:
            self._deployment_strategy.run(script_path)
        except SyntaxError as e:
            self._handle_syntax_error(e)
            

        self._client = TrainingClient(
            producer, consumer,
            graph_builder=self._graph_builder,
            on_receive_graph=self._on_receive_graph,
            on_userland_error=self._on_userland_error,
            on_state_changed=self._on_training_state_changed,
            on_training_ended=self._on_training_ended,            
            on_server_timeout=self._on_server_timeout,
            on_userland_timeout=self._on_userland_timeout,
            on_log_message=self._on_log_message,
            server_timeout=self._server_timeout
        )
        
        client_step = self._client.run_stepwise()
        yield from self._await_status_ready(client_step)

        self.request_start()
        
        yield from self._await_status_active(client_step)
        self._time_started = time.time()
        
        yield from self._await_status_done(client_step)

        if auto_close:
            self.request_close()
            logger.info("Sent request for auto-close")
            
        yield from self._await_status_exit(client_step)

    def _handle_syntax_error(self, exception):
        node, true_lineno = self._line_to_node_map.get(exception.lineno, (None, None))
        
        message = f'SyntaxError:\n\n' + \
                  f'File "{exception.filename}", line {exception.lineno}, offset {exception.offset}\n' + \
                  f'origin {node.id_}, line {true_lineno} [{node.type_}]\n' +\
                  f'  {exception.text}\n'
        error = UserlandError(node.id_, node.type_, exception.lineno, message)
        self._handle_userland_error(error)


    def _handle_name_error(self, exception):
        node, true_lineno = self._line_to_node_map.get(exception.lineno, (None, None))
        
        message = f'SyntaxError:\n\n' + \
                  f'File "{exception.filename}"\n' + \
                  f'origin {node.id_}, line {true_lineno} [{node.type_}]\n' +\
                  f'  {exception.text}\n'
        error = UserlandError(node.id_, node.type_, exception.lineno, message)
        self._handle_userland_error(error)

        
    def _handle_userland_error(self, error):
        if self._use_sentry:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('error-type', 'userland-error')
                scope.level = 'info'
                sentry_sdk.capture_message(error.format())

        logger.info('Training stopped because of userland error:\n' + error.format())
        if self._issue_handler is not None:
            self._issue_handler.put_error(error.format())

    @property
    def training_session_id(self):
        return self._training_session_id

    @property
    def is_closed(self):
        return self.is_closed_by_server or self.is_closed_by_force

    @property
    def is_closed_by_server(self):
        return self._closed_by_server

    @property
    def is_closed_by_force(self):
        return self._closed_by_force

    @property
    def has_client(self):
        return self._client is not None

    def _await_status(self, client_step, expected_states, sleep_interval=0.5, by_force_only=False):
        is_closed = lambda: self.is_closed_by_force if by_force_only else self.is_closed

        t0 = time.perf_counter()
        s0 = self._client.training_state
        
        while self._client.training_state not in expected_states and not is_closed():
            next(client_step)
            time.sleep(sleep_interval)
            yield

        logger.info(
            f"Awaiting status completed with transition: {s0} -> {self._client.training_state}. "
            f"is_closed: {self.is_closed}, is_closed_by_force: {self.is_closed_by_force}. "
            f"Duration: {time.perf_counter() - t0}"
        )

    def _await_status_ready(self, client_step):
        yield from self._await_status(client_step, [State.READY])

    def _await_status_active(self, client_step):
        yield from self._await_status(client_step, State.active_states)        

    def _await_status_done(self, client_step):
        yield from self._await_status(client_step, State.done_states, sleep_interval=1.0)                

    def _await_status_exit(self, client_step):
        yield from self._await_status(client_step, State.exit_states, sleep_interval=1.0, by_force_only=True)

    def _on_training_state_changed(self, new_state):
        logger.info(f"Training server entered state {new_state}")

        if new_state == State.CLOSING:
            self._client.shutdown()            
            self._closed_by_server = True
            logger.info(f"Core closed by server. Training session: [{self._training_session_id}]")            
        
    def _on_userland_timeout(self):
        if self._issue_handler is not None:
            self._issue_handler.put_error('Training stopped because a training step too long!')
        logger.info('Training stopped because a training step too long!')

    def _on_server_timeout(self):
        if self._issue_handler is not None:
            with self._issue_handler.create_issue('Training server timed out!') as issue:
                self._issue_handler.put_error(issue.frontend_message)
                logger.error(issue.internal_message)
        else:
            logger.error("Training server timed out!")

        self.force_close(timeout=1)

    @property
    def last_graph(self):
        return self._last_graph

    @property
    def graph_spec(self):
        return self._graph_spec
    
    def _on_receive_graph(self, graph):
        self._graphs.append(graph)
        self._last_graph = graph

        if not self._collected_start_metrics and self._last_graph is not None and self._running_mode == 'training':
            dataevents.collect_start_metrics(self._graph_spec, self._last_graph, self._training_session_id, self._model_id)        
            self._collected_start_metrics = True        

    def _on_training_ended(self, session_info, end_state):
        if self._graph_spec is not None and self._running_mode == 'training':
            dataevents.collect_end_metrics(self._graph_spec, self._last_graph, self._training_session_id, session_info, self._model_id, end_state)
            
        self._time_ended = time.time()
        if self._paused_time_stamp is not None and self._running_mode == 'training':
            self._time_paused += self._time_ended - self._paused_time_stamp
            self._paused_time_stamp = None
            
    def _on_log_message(self, level, message):
        if self._issue_handler is None:
            return

        if level == 'WARNING':            
            self._issue_handler.put_info(message) # TODO: more intuitive naming
        elif level in ['ERROR', 'CRITICAL']:
            self._issue_handler.put_error(message)            
            
        self._issue_handler.put_log(message)
        
    def _create_script(self, graph_spec, training_session_id, topic_generic, topic_snapshots, userland_timeout):
        try:
            code, self._line_to_node_map = self._script_factory.make(graph_spec, training_session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)
        except FetchParameterError as e:
            error = UserlandError(
                e.layer_id, e.layer_type,
                line_number=None,
                message=f"Couldn't fetch parameter '{e.parameter}'. Verify that the layer has been applied.",
                code=None
            )
            self._handle_userland_error(error)
            
        with open(training_script_name, 'wt') as f:
            f.write(code)
            f.flush()
        return training_script_name

    def _on_userland_error(self, exception: str, traceback_frames: List[TracebackFrame]):
        message = str(exception) +'\n\n'
        collect = False
        last_node = None
        last_lineno = None

        for frame in traceback_frames:
            node, true_lineno = self._line_to_node_map.get(frame.lineno, (None, None))
            
            if not collect and frame.filename == training_script_name:
                collect = True
            if not collect:
                continue
                
            if frame.filename == training_script_name and node is not None:
                last_node = node
                last_lineno = true_lineno

                message +=  f'File "{frame.filename}", line {frame.lineno}, in {frame.name}, ' + \
                            f'origin {node.id_}, line {true_lineno} [{node.type_}]\n' +\
                            f'  {frame.line}\n'
            else:
                message +=  f'File "{frame.filename}", line {frame.lineno}, in {frame.name}\n' + \
                            f'  {frame.line}\n'
        
        if last_node:
            error = UserlandError(last_node.id_, last_node.type_, last_lineno, message)
        else:
            error = UserlandError(node.id_, node.type_, frame.lineno, message)

        self._handle_userland_error(error)
        
    @property
    def graphs(self) -> List[Graph]:
        copy_graph = self._graphs.copy()
        self._graphs = []
        return copy_graph

    def force_close(self, timeout=240):
        self.request_close()

        if not self._deployment_strategy.shutdown(timeout=timeout):
            logger.warning(f"Deployment did not shut down within {timeout}s. Proceeding anyway!")

        self._closed_by_force = True
        logger.info("Force closed core")

    def request_start(self):
        self._client.request_start()
        logger.info("Requested start")

    def request_close(self, is_auto=False):
        self._client.request_close()
        logger.info("Requested close")
        
    def request_pause(self):
        if self._client is not None:
            self._client.request_pause()
            self._paused_time_stamp = time.time()
        else:
            logger.warning("Requested pause but training client not set!!")

    def request_unpause(self):
        self._client.request_resume()
        self._time_paused += time.time() - self._paused_time_stamp
        self._paused_time_stamp = None
    
    def request_headless_activate(self):
        self._client.request_headless_activate()
        
    def request_headless_deactivate(self):
        self._client.request_headless_deactivate()

    def request_export(self, path: str, mode: str):
        self._client.request_export(path, mode)
        logger.debug(f"Requested export with path: {path}, mode: {mode}")  

    def request_advance_testing(self):
        self._client.request_advance_testing()

    def request_stop(self):
        self._client.request_stop()

    @property
    def is_training_running(self):
        if self._client is None:
            return False
        return self._client.training_state in State.running_states

    @property
    def is_training_paused(self):
        if self._client is None:
            return False
        return self._client.training_state in State.paused_states        

    @property
    def training_state(self):
        return self._client.training_state

    @property
    def training_ended_time(self):
        return self._time_ended

    @property
    def training_duration(self):
        if self._time_started is None:
            return None
        else:
            if self._paused_time_stamp is None:
                if self._time_ended is None:
                    return time.time() - self._time_started - self._time_paused
                else:
                    return self._time_ended - self._time_started - self._time_paused
            else:
                return self._paused_time_stamp - self._time_started - self._time_paused


    @property
    @deprecated
    def is_paused(self):
        return self.is_training_paused

    @property
    @deprecated
    def is_running(self):
        return self.is_training_running
    
    @deprecated
    def close(self, wait_for_deployment=False):
        timeout = None if wait_for_deployment else 1
        self.force_close(timeout=timeout)
        
    @deprecated
    def stop(self):
        self.request_stop()
        
    @deprecated
    def export(self, path, mode):
        self.request_export(path, mode)
        
    @deprecated
    def advance_testing(self):
        self.request_advance_testing()
    
    @deprecated
    def pause(self):
        self.request_pause()

    @deprecated
    def unpause(self):
        self.request_unpause()

    @deprecated
    def headlessOff(self):
        self.request_headless_deactivate()

    @deprecated
    def headlessOn(self):
        self.request_headless_activate()        
            

    

        
