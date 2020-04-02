import os
import sys
import time
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
import multiprocessing
from typing import Dict, List, Callable
from abc import ABC, abstractmethod
from queue import Queue


from perceptilabs.issues import IssueHandler, UserlandError
from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.api.mapping import ByteMap
from perceptilabs.core_new.communication.status import *
from perceptilabs.core_new.communication import TrainingClient, State
from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.communication.deployment import ThreadStrategy, DeploymentStrategy

log = logging.getLogger(__name__)


def find_free_port(count=1):
    """Find free port(s) and then close. WARNING: this approach is subject to race conditions!"""

    sockets = []
    for _ in range(count):
        s = socket.socket()
        s.bind(('', 0)) # Bind to a free port
        sockets.append(s)
        
    ports = []
    for s in sockets:
        ports.append(s.getsockname()[1])
        s.close()
        
    if len(ports) == 1:
        return ports[0]
    else:
        return tuple(ports)    
    
    
class Core:
    def __init__(self, graph_builder: GraphBuilder, script_factory: ScriptFactory, issue_handler: IssueHandler=None, max_server_response_time=20, max_training_step_time=15, deployment_strategy=None):
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._graphs = []
        self._issue_handler = issue_handler

        self._deployment_strategy = deployment_strategy or ThreadStrategy()
        
        self._is_running = threading.Event()
        self._is_running.clear()
        self._training_client = None

        self._remote_is_paused = False
        self._max_server_response_time = max_server_response_time
        self._max_training_step_time = max_training_step_time
        
    def run(self, graph_spec: JsonNetwork, session_id: str=None, on_iterate: List[Callable]=None, auto_stop=False):
        on_iterate = on_iterate or []
        try:
            self._run_internal(
                graph_spec,
                session_id=session_id,
                on_iterate=on_iterate,
                auto_stop=auto_stop
            )
        except Exception as e:
            log.exception("Exception in core.run")
            raise
        finally:
            log.info(f"Stopping core with session id {session_id}")
            self.stop()                

    def _run_internal(self, graph_spec, session_id=None, on_iterate=None, auto_stop=False):
        session_id = session_id or uuid.uuid4().hex
        graph = self._graph_builder.build_from_spec(graph_spec)
        port1, port2 = find_free_port(count=2)        
        code, line_to_node_map = self._script_factory.make(graph, session_id, port1, port2, max_training_step_time=self._max_training_step_time)

        script_path = f'training_script.py'
        with open(script_path, 'wt') as f:
            f.write(code)
            f.flush()
        #shutil.copy(script_path, 'training_script.py')            

        self._deployment_strategy.run(script_path)
        time.sleep(3) # Give TrainingServer some time to start.. 

        def on_server_timeout():
            if self._issue_handler is not None:
                with self._issue_handler.create_issue('Training server timed out! Shutting down core') as issue:
                    self._issue_handler.put_error(issue.frontend_message)
                    log.error(issue.internal_message)
            else:
                log.error("Training server timed out! Shutting down core")
                
        def on_userland_error(exception, tb_list):
            message = ''
            collect = False
            for frame in tb_list:
                node, true_lineno = line_to_node_map.get(frame.lineno, (None, None))

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
            with sentry_sdk.push_scope() as scope:
                scope.set_tag('error-type', 'userland-error')
                scope.level = 'info'
                sentry_sdk.capture_message(error.format())
            
            log.info('Userland error:\n' + error.format())
            if self._issue_handler is not None:
                self._issue_handler.put_error(error.format())          

        def on_log_message(message):
            log.info("Userland: " + message)

        def on_server_killed():
            if self._issue_handler is not None:
                self._issue_handler.put_error('Server killed because a training step too long!')
            log.error('Server killed because a training step too long!')
            
        self._training_client = training_client = TrainingClient(
            port1, port2,
            graph_builder=self._graph_builder,
            on_userland_error=on_userland_error,
            on_server_timeout=on_server_timeout,
            on_server_killed=on_server_killed,
            on_log_message=on_log_message,
            max_response_time=self._max_server_response_time
        )

        training_client.connect()

                
        counter = 0        
        while training_client.remote_status == None:
            if counter % 100 == 0:
                log.info("Waiting for remote status != None")
            time.sleep(0.1)
            counter += 1
        
        training_client.request_start()
        counter = 0
        while training_client.remote_status == State.READY:
            if counter % 100 == 0:
                log.info("Waiting for remote status READY")
            time.sleep(0.1)
            counter += 1

        if training_client.remote_status == State.RUNNING:
            log.info(f"Training client connected to server. Session id: {session_id}")
        else:
            raise RuntimeError(f"Expected status {State.RUNNING}, got {training_client.remote_status}!")

        self._is_running.set()        
        counter = 0
        while training_client.remote_status in [State.RUNNING, State.PAUSED]:
            self._remote_is_paused = training_client.remote_status == State.PAUSED
            
            if counter % 30 == 0:
                log.info(f"Training status: {training_client.remote_status}. Graph count: {len(self._graphs)}")
                         
            self._graphs = training_client.graphs.copy()
            time.sleep(0.1)
            counter += 1

        self._remote_is_paused = False
    
        if auto_stop:
            training_client.request_stop()            
                        
        counter = 0
        while training_client.remote_status == State.IDLE:
            if counter % 100 == 0:
                log.info("Idle. Graph count: " + str(len(self._graphs)))                     
            time.sleep(0.5)

        if training_client.remote_status == State.DONE:
            log.info("Done!: ")
        elif training_client.remote_status == None:
            log.info("Done, but with none! ")            

        training_client.stop()

            
    @property
    def graphs(self) -> List[Graph]:
        return self._graphs.copy()

    def stop(self):
        #if self._client is not None:
        #    self._client.send_event('on_stop')
        #    self._client.stop()
        #    log.info(f"Sent stop command to deployed core")                        
            
        self._is_running.clear()
        
    def pause(self):
        if self._training_client is not None:
            self._training_client.request_pause()
        else:
            log.warning("Requested pause but training client not set!!")

    def unpause(self):
        if self._training_client is not None:
            self._training_client.request_resume()
    
    def headlessOn(self):
        if self._training_client is not None:
            self._training_client.request_headless_activate()
        
    def headlessOff(self):
        if self._training_client is not None:
            self._training_client.request_headless_deactivate()

    def export(self, path: str, mode: str):
        log.debug(f"Export path: {path}, mode: {mode}, client: {self._client}")
        
        if self._training_client is not None:            
            self._client.request_export(path, mode)
        else:
            log.warning("Client is none. on_export not called!")

    @property
    def is_running(self):
        return self._is_running.is_set() 

    @property
    def is_paused(self):
        return self.is_running and self._remote_is_paused
            
    @property
    def remote_status(self):
        if self._training_client is not None and self._is_running.is_set():
            self._training_client.remote_status
        else:
            return None
        
        

    
