
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
import subprocess
import sentry_sdk
import collections
import multiprocessing
from typing import Dict, List, Callable
from abc import ABC, abstractmethod
from queue import Queue


from perceptilabs.utils import deprecated
from perceptilabs.issues import IssueHandler, UserlandError
from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.api.mapping import ByteMap
from perceptilabs.core_new.communication import TrainingClient, State
from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.communication.deployment import ThreadStrategy, DeploymentStrategy
from perceptilabs.messaging import MessageConsumer, MessageProducer          

log = logging.getLogger(__name__)


class CoreState(enum.Enum):
    INITIALIZING = 0
    TRAINING = 1
    IDLE = 2
    SERVER_TIMEOUT = 3
    USERLAND_TIMEOUT = 4
    USERLAND_ERROR = 5
    CLOSED = 6


class Core:
    def __init__(self, graph_builder: GraphBuilder, script_factory: ScriptFactory, issue_handler: IssueHandler=None, server_timeout=610, userland_timeout=600, deployment_strategy=None, use_sentry=False):
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._graphs = collections.deque(maxlen=500)
        self._issue_handler = issue_handler
        self._use_sentry = use_sentry

        self._deployment_strategy = deployment_strategy or ThreadStrategy()

        self._server_timeout = server_timeout
        self._userland_timeout = userland_timeout

        self._client = None
        self._closed_by_server = False
        self._closed_by_force = False        

        
    ''' 
    def run(self, graph_spec: JsonNetwork, session_id: str=None, on_iterate: List[Callable]=None, auto_close=False):
        on_iterate = on_iterate or []
        try:
            self._run_internal(
                graph_spec,
                session_id=session_id,
                on_iterate=on_iterate,
                auto_close=auto_close
            )
        except Exception as e:
            log.exception("Exception in core.run")
            raise
        finally:
            #log.info(f"Closing core with session id {session_id}")
            #self.close()                
            pass
    '''

    def run(self, graph_spec: JsonNetwork, session_id: str=None, on_iterate: List[Callable]=None, auto_close=False):
        step = self.run_stepwise(graph_spec, session_id=session_id, auto_close=auto_close)
        for counter, _ in enumerate(step):
            if counter % 100 == 0:
                log.debug(f"Running step {counter}")
        
    def run_stepwise(self, graph_spec, session_id=None, auto_close=False):
        session_id = session_id or uuid.uuid4().hex        
        topic_generic = f'generic-{session_id}'.encode()    
        topic_snapshots = f'snapshots-{session_id}'.encode()
        
        graph = self._graph_builder.build_from_spec(graph_spec)        
        script_path = self._create_script(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)
        self._deployment_strategy.run(script_path)

        consumer = MessageConsumer([topic_generic, topic_snapshots])
        producer = MessageProducer(topic_generic)
        log.info(f"Instantiated message producer/consumer pairs for topics {topic_generic} and {topic_snapshots} for session {session_id}")

        self._client = TrainingClient(
            producer, consumer,
            graph_builder=self._graph_builder,
            on_receive_graph=self._on_receive_graph,
            on_userland_error=self._on_userland_error,
            on_state_changed=self._on_training_state_changed,
            on_server_timeout=self._on_server_timeout,
            on_userland_timeout=self._on_userland_timeout,
            on_log_message=self._on_log_message,
            server_timeout=self._server_timeout
        )
        
        client_step = self._client.run_stepwise()
        yield from self._await_status_ready(client_step)
        
        self.request_start()        
        yield from self._await_status_active(client_step)
        yield from self._await_status_done(client_step)

        if auto_close:
            self.request_close()
            log.info("Sent request for auto-close")
            
        yield from self._await_status_exit(client_step)

    @property
    def is_closed(self):
        return self.is_closed_by_server or self.is_closed_by_force

    @property
    def is_closed_by_server(self):
        return self._closed_by_server

    @property
    def is_closed_by_force(self):
        return self._closed_by_force
        
    def _await_status_ready(self, client_step):
        while self._client.training_state != State.READY and not self.is_closed:
            next(client_step)
            time.sleep(0.5)            
            yield

    def _await_status_active(self, client_step):            
        while (self._client.training_state not in State.active_states) and not self.is_closed:
            next(client_step)
            time.sleep(0.5)            
            yield

    def _await_status_done(self, client_step):
        while (self._client.training_state not in State.done_states) and not self.is_closed:
            next(client_step)
            time.sleep(1.0)            
            yield

    def _await_status_exit(self, client_step):
        while (self._client.training_state not in State.exit_states) and not self.is_closed_by_force:
            next(client_step)
            time.sleep(1.0)            
            yield

    def _on_training_state_changed(self, new_state):
        log.info(f"Training server entered state {new_state}")            
        
        if new_state in State.exit_states:
            self._closed_by_server = True

    def _on_userland_timeout(self):
        if self._issue_handler is not None:
            self._issue_handler.put_error('Training stopped because a training step too long!')
        log.info('Training stopped because a training step too long!')

    def _on_server_timeout(self):
        if self._issue_handler is not None:
            with self._issue_handler.create_issue('Training server timed out!') as issue:
                self._issue_handler.put_error(issue.frontend_message)
                log.error(issue.internal_message)
        else:
            log.error("Training server timed out!")

        self.force_close(timeout=1)
    
    def _on_receive_graph(self, graph):
        self._graphs.append(graph)
        
    def _on_log_message(self, message):
        pass    

    def _create_script(self, graph, session_id, topic_generic, topic_snapshots, userland_timeout):
        code, self._line_to_node_map = self._script_factory.make(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)
        
        script_path = f'training_script.py'
        with open(script_path, 'wt') as f:
            f.write(code)
            f.flush()
        return script_path

    '''
    def _run_internal(self, graph_spec, session_id=None, on_iterate=None, auto_close=False):
        session_id = session_id or uuid.uuid4().hex
        log.info(f"Entered 'run internal' for core with session id {session_id}")
        
        graph = self._graph_builder.build_from_spec(graph_spec)
        log.info(f"Built graph for session id {session_id}")        
        
        topic_generic = f'generic-{session_id}'.encode()    
        topic_snapshots = f'snapshots-{session_id}'.encode()    
        
        code, self._line_to_node_map = self._script_factory.make(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)
        log.info(f"Generated code for session id {session_id}")        
        
        script_path = f'training_script.py'
        with open(script_path, 'wt') as f:
            f.write(code)
            f.flush()
        #shutil.copy(script_path, 'training_script.py')            

        self._deployment_strategy.run(script_path)
        log.info(f"Ran deployment strategy {self._deployment_strategy} for session {session_id}")
        
        #time.sleep(3) # Give TrainingServer some time to start.. 

        def on_server_timeout():
            if self._issue_handler is not None:
                with self._issue_handler.create_issue('Training server timed out! Shutting down core') as issue:
                    self._issue_handler.put_error(issue.frontend_message)
                    log.error(issue.internal_message)
            else:
                log.error("Training server timed out! Shutting down core")
            self._is_running = False
            
                
        def on_log_message(message):
            log.info("Userland: " + message)

        def on_userland_timeout():
            if self._issue_handler is not None:
                self._issue_handler.put_error('Training stopped because a training step too long!')
            log.error('Training stopped because a training step too long!')
            self._is_running = False            

        consumer = MessageConsumer([topic_generic, topic_snapshots])
        producer = MessageProducer(topic_generic)
        log.info(f"Instantiated message producer/consumer pairs for topics {topic_generic} and {topic_snapshots} for session {session_id}")                
        
        log.info("Creating training client")            
        client = self._client = TrainingClient(
            producer, consumer,
            graph_builder=self._graph_builder,
            on_receive_graph=self._on_receive_graph,
            on_userland_error=self._on_userland_error,
            on_server_timeout=on_server_timeout,
            on_userland_timeout=on_userland_timeout,
            on_log_message=on_log_message,
            server_timeout=self._server_timeout
        )
        log.info(f"Instantiated training client for session {session_id}")                
        
        update_client = client.run_stepwise() # Establish connection and set up generator
        self._is_running = True

        counter = 0        
        while client.training_state == None and self._is_running:
            next(update_client) 
            if counter % 100 == 0:
                log.info("Waiting for remote status != None")
            time.sleep(0.1)
            counter += 1
        log.info(f"Received training state {client.training_state} for session {session_id}")                            
            
        client.request_start()
        log.info(f"Requested training start in for session {session_id}")
        
        counter = 0
        while client.training_state == State.READY and self._is_running:
            next(update_client)             
            if counter % 100 == 0:
                log.info("Waiting for remote status READY")
            time.sleep(0.1)
            counter += 1
        log.info(f"Received training state {client.training_state} for session id {session_id}")                                        

        if client.training_state in State.active_states:
            log.info(f"Training running. State: {client.training_state}. Session id: {session_id}")
        else:
            raise RuntimeError(f"Expected an active state, got {client.training_state}!")

        self._is_running = True
        counter = 0
        while client.training_state in State.active_states and self._is_running:
            next(update_client)                         
            
            if counter % 30 == 0:
                log.info(f"Training state: {client.training_state}. Graph count: {len(self._graphs)}")                         
            time.sleep(0.1)
            counter += 1

        if not self._is_running:
            return client.training_state
        
        if not auto_close:
            counter = 0
            while client.training_state in State.idle_states and self._is_running:
                next(update_client)                                     
                if counter % 20 == 0:
                    log.info("Idle. Graph count: " + str(len(self._graphs)))                     
                time.sleep(1.0)
                
        log.info("Exiting run internal with state " + str(client.training_state))
        return client.training_state
    
    def _on_receive_graph(self, graph):
        self._graphs.append(graph)        
    '''
    def _on_userland_error(self, exception, traceback_frames):
        message = ''
        collect = False
        for frame in traceback_frames:
            node, true_lineno = self._line_to_node_map.get(frame.lineno, (None, None))
            
            if not collect and frame.filename == 'training_script.py':
                collect = True
            if not collect:
                continue
                
            if frame.filename == 'training_script.py' and node is not None:
                message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}, ' + \
                           f'origin {node.layer_id}:{true_lineno} [{node.layer_type}]\n' +\
                           f'  {frame.line}\n'
            else:
                message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}\n' + \
                           f'  {frame.line}\n'
                    
        error = UserlandError(node.layer_id, node.layer_type, frame.lineno, message)

        if self._use_sentry:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('error-type', 'userland-error')
                scope.level = 'info'
                sentry_sdk.capture_message(error.format())

        log.info('Training stopped because of userland error:\n' + error.format())
        if self._issue_handler is not None:
            self._issue_handler.put_error(error.format())

    @property
    def graphs(self) -> List[Graph]:
        copy_graph = self._graphs.copy()
        self._graphs = []
        return copy_graph

    def force_close(self, timeout=240):
        self.request_close()

        if not self._deployment_strategy.shutdown(timeout=timeout):
            log.warning("Failed to shutdown deployment!")

        self._closed_by_force = True
        log.info("Force closed core")

    def request_start(self):
        self._client.request_start()

    def request_close(self):
        self._client.request_close()
        
    def request_pause(self):
        if self._client is not None:
            self._client.request_pause()
        else:
            log.warning("Requested pause but training client not set!!")

    def request_unpause(self):
        self._client.request_resume()
    
    def request_headless_activate(self):
        self._client.request_headless_activate()
        
    def request_headless_deactivate(self):
        self._client.request_headless_deactivate()

    def request_export(self, path: str, mode: str):
        self._client.request_export(path, mode)
        log.debug(f"Requested export with path: {path}, mode: {mode}")        

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
            

    
