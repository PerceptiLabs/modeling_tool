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


from perceptilabs.utils import deprecated
from perceptilabs.issues import IssueHandler, UserlandError
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.utils import TracebackFrame
from perceptilabs.core_new.layers import TrainingSupervised, TrainingReinforce, TrainingRandom
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.communication import TrainingClient, State
from perceptilabs.core_new.layers.script import ScriptFactory, FetchParameterError
from perceptilabs.core_new.communication.deployment import ThreadStrategy, DeploymentStrategy
from perceptilabs.messaging import MessagingFactory
from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)



def make_graph_spec_conform_to_schema(graph_spec):
    graph_spec = graph_spec['Layers'] 

    edges = []
    nodes = []
    for from_id, layer_spec in graph_spec.items():
        # Nodes. For now, we don't include any detailed parameters...
        #layer_spec = layer_spec['Info']
        
        from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE        
        def_ = DEFINITION_TABLE.get(layer_spec['Type'])        
        node = {
            'type': def_.template_macro,
            'id': from_id,
        }
        nodes.append(node)
        
        # Edges
        fwd_cons = [layer_id for layer_id, _ in layer_spec['forward_connections']]
        for to_id in fwd_cons:
            edges.append([from_id, to_id])

    return {
        'nodes': nodes,
        'edges': edges
    }


def collect_start_metrics(graph_spec, graph, training_sess_id):
    """ quick-fix for collecting start metrics. update when newer version of core is merged"""
    import numpy as np

    n_params = 0
    # TODO: training layer parameter called n_parameters for proper generalization...
    for weights_dict in graph.active_training_node.layer.layer_weights.values():
        for w in weights_dict.values():
            n_params += np.prod(w.shape)

    for biases_dict in graph.active_training_node.layer.layer_biases.values():
        for b in biases_dict.values():
            n_params += np.prod(b.shape)

    formatted_graph = make_graph_spec_conform_to_schema(graph_spec)            

    data_logger.info(
        "training_started",
        extra={
            'namespace': dict(
                training_session_id=training_sess_id,        
                graph_spec=formatted_graph,
                n_parameters=int(n_params)
            )
        }
    )
    


def collect_end_metrics(graph_spec, graph, training_sess_id, session_info):
    """ quick-fix for collecting start metrics. update when newer version of core is merged"""
    import numpy as np

    n_params = 0
    # TODO: training layer parameter called n_parameters for proper generalization...
    for weights_dict in graph.active_training_node.layer.layer_weights.values():
        for w in weights_dict.values():
            n_params += np.prod(w.shape)

    for biases_dict in graph.active_training_node.layer.layer_biases.values():
        for b in biases_dict.values():
            n_params += np.prod(b.shape)

    formatted_graph = make_graph_spec_conform_to_schema(graph_spec)
    
    data_meta_list = []
    for node in graph.data_nodes:
        data_meta = {
            'layer_id': node.layer_id,
        }
        # TODO: remove hasattr when changes to DataLayer have been merged
        if node is not None and hasattr(node.layer, 'size_training'):
            data_meta.update({
                'training_set_size': int(node.layer.size_training),
                'validation_set_size': int(node.layer.size_validation),
                'testing_set_size': int(node.layer.size_testing)
            })
        data_meta_list.append(data_meta)

    data_logger.info(
        "training_ended",
        extra={
            'namespace': dict(
                training_session_id=training_sess_id,        
                graph_spec=formatted_graph,
                n_parameters=int(n_params),
                time_total=session_info['time_total'],
                cycle_state_initial=session_info['cycle_state_initial'],
                cycle_state_final=session_info['cycle_state_final'],
                cycle_time_process_messages=session_info['cycle_time_process_messages'],
                cycle_time_training_step=session_info['cycle_time_training_step'],
                cycle_time_send_snapshot=session_info['cycle_time_send_snapshot'],
                cycle_time_total=session_info['cycle_time_total'],
                mem_phys_total=session_info['mem_phys_total'],
                cycle_mem_phys_available=session_info['cycle_mem_phys_available'],
                mem_swap_total=session_info['mem_swap_total'],
                cycle_mem_swap_free=session_info['cycle_mem_swap_free'],
                data_meta=data_meta_list
            )
        }
    )


class Core:
    def __init__(self, graph_builder: GraphBuilder, script_factory: ScriptFactory, messaging_factory: MessagingFactory, issue_handler: IssueHandler=None, server_timeout=610, userland_timeout=600, deployment_strategy=None, use_sentry=False, samplers=None):
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._messaging_factory = messaging_factory
        self._graphs = collections.deque(maxlen=500)
        self._last_graph = None
        self._graph_spec = None
        self._issue_handler = issue_handler
        self._use_sentry = use_sentry
        self._samplers = samplers or []

        #from perceptilabs.insights.dataset import DatasetDistribution
        #self._dataset_distr = DatasetDistribution()
        
        self._deployment_strategy = deployment_strategy or ThreadStrategy()

        self._server_timeout = server_timeout
        self._userland_timeout = userland_timeout

        self._client = None
        self._closed_by_server = False
        self._closed_by_force = False
        self._collected_start_metrics = False
        
    def run(self, graph_spec, session_id: str=None, on_iterate: List[Callable]=None, auto_close=False):
        self._graph_spec = graph_spec
        step = self.run_stepwise(graph_spec, session_id=session_id, auto_close=auto_close)
        for counter, _ in enumerate(step):
            if counter % 100 == 0:
                logger.debug(f"Running step {counter}")
        
    def run_stepwise(self, graph_spec, session_id=None, auto_close=False):
        self._session_id = session_id = session_id or uuid.uuid4().hex        
        topic_generic = f'generic-{session_id}'.encode()    
        topic_snapshots = f'snapshots-{session_id}'.encode()
        
        graph = self._graph_builder.build_from_spec(graph_spec)        
        script_path = self._create_script(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)

        try:
            self._deployment_strategy.run(script_path)
        except SyntaxError as e:
            self._handle_syntax_error(e)
            
        producer = self._messaging_factory.make_producer(topic_generic)        
        consumer = self._messaging_factory.make_consumer([topic_generic, topic_snapshots])
        logger.info(f"Instantiated message producer/consumer pairs for topics {topic_generic} and {topic_snapshots} for session {session_id}")

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
                  f'origin {node.layer_id}, line {true_lineno} [{node.layer_type}]\n' +\
                  f'  {exception.text}\n'
        error = UserlandError(node.layer_id, node.layer_type, exception.lineno, message)
        self._handle_userland_error(error)


    def _handle_name_error(self, exception):
        node, true_lineno = self._line_to_node_map.get(exception.lineno, (None, None))
        
        message = f'SyntaxError:\n\n' + \
                  f'File "{exception.filename}"\n' + \
                  f'origin {node.layer_id}, line {true_lineno} [{node.layer_type}]\n' +\
                  f'  {exception.text}\n'
        error = UserlandError(node.layer_id, node.layer_type, exception.lineno, message)
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
        logger.info(f"Training server entered state {new_state}")
        
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
    
    def _on_receive_graph(self, graph):
        self._graphs.append(graph)
        
        self._last_graph = graph

        #if self._dataset_distr is not None:
        #    data_node_ids = [n.layer_id for n in graph.data_nodes if n != graph.active_training_node]
        #    batches = {id_: graph.active_training_node.layer.layer_outputs[id_] for id_ in data_node_ids}
        #    self._dataset_distr.draw_sample(batches)
        
        if not self._collected_start_metrics and self._last_graph is not None:
            collect_start_metrics(self._graph_spec, self._last_graph, self._session_id)        
            self._collected_start_metrics = True        

    def _on_training_ended(self, session_info):
        if self._graph_spec is not None:
            collect_end_metrics(self._graph_spec, self._last_graph, self._session_id, session_info)
        self._time_ended = time.time()
        
    def _on_log_message(self, message):
        pass    

    def _create_script(self, graph, session_id, topic_generic, topic_snapshots, userland_timeout):

        try:
            code, self._line_to_node_map = self._script_factory.make(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)
        except FetchParameterError as e:
             error = UserlandError(
                 e.layer_id, e.layer_type,
                 line_number=None,
                 message=f"Couldn't fetch parameter '{e.parameter}'. Verify that the layer has been applied.",
                 code=None
             )
             self._handle_userland_error(error)             
             
        script_path = f'training_script.py'
        with open(script_path, 'wt') as f:
            f.write(code)
            f.flush()
        return script_path

    def _on_userland_error(self, exception, traceback_frames):
        message = str(exception) +'\n\n'
        collect = False
        last_node = None
        last_lineno = None

        for frame in traceback_frames:
            node, true_lineno = self._line_to_node_map.get(frame.lineno, (None, None))
            
            if not collect and frame.filename == 'training_script.py':
                collect = True
            if not collect:
                continue
                
            if frame.filename == 'training_script.py' and node is not None:
                last_node = node
                last_lineno = true_lineno

                message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}, ' + \
                           f'origin {node.layer_id}, line {true_lineno} [{node.layer_type}]\n' +\
                           f'  {frame.line}\n'
            else:
                message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}\n' + \
                           f'  {frame.line}\n'
        
        if last_node:
            error = UserlandError(last_node.layer_id, last_node.layer_type, last_lineno, message)
        else:
            error = UserlandError(node.layer_id, node.layer_type, frame.lineno, message)

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

    def request_close(self):
        self._client.request_close()
        logger.info("Requested close")
        
    def request_pause(self):
        if self._client is not None:
            self._client.request_pause()
        else:
            logger.warning("Requested pause but training client not set!!")

    def request_unpause(self):
        self._client.request_resume()
    
    def request_headless_activate(self):
        self._client.request_headless_activate()
        
    def request_headless_deactivate(self):
        self._client.request_headless_deactivate()

    def request_export(self, path: str, mode: str):
        self._client.request_export(path, mode)
        logger.debug(f"Requested export with path: {path}, mode: {mode}")        

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
        if self._time_ended is None:
            return time.time() - self._time_started
        else:
            return self._time_ended - self._time_started

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
            

    

        
