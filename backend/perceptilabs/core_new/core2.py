
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
import collections
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
from perceptilabs.messaging import MessageConsumer, MessageProducer          

log = logging.getLogger(__name__)
    
    
class Core:
    def __init__(self, graph_builder: GraphBuilder, script_factory: ScriptFactory, issue_handler: IssueHandler=None, server_timeout=20, userland_timeout=30, deployment_strategy=None, use_sentry=False):
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._graphs = collections.deque(maxlen=500)
        self._issue_handler = issue_handler
        self._use_sentry = use_sentry

        self._deployment_strategy = deployment_strategy or ThreadStrategy()

        self._server_timeout = server_timeout
        self._userland_timeout = userland_timeout

        self._client = None
        self._is_running = False
        
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

    def _run_internal(self, graph_spec, session_id=None, on_iterate=None, auto_close=False):
        session_id = session_id or uuid.uuid4().hex
        log.info(f"Running core with session id {session_id}")        
        graph = self._graph_builder.build_from_spec(graph_spec)

        topic_generic = f'generic-{session_id}'.encode()    
        topic_snapshots = f'snapshots-{session_id}'.encode()    
        
        code, self._line_to_node_map = self._script_factory.make(graph, session_id, topic_generic, topic_snapshots, userland_timeout=self._userland_timeout)

        script_path = f'training_script.py'
        with open(script_path, 'wt') as f:
            f.write(code)
            f.flush()
        #shutil.copy(script_path, 'training_script.py')            

        log.info("Running deployment")
        self._deployment_strategy.run(script_path)
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

        update_client = client.run_stepwise() # Establish connection and set up generator
        self._is_running = True

        counter = 0        
        while client.training_state == None and self._is_running:
            next(update_client) 
            if counter % 100 == 0:
                log.info("Waiting for remote status != None")
            time.sleep(0.1)
            counter += 1

        log.info("Requesting training start")
        client.request_start()
        counter = 0
        while client.training_state == State.READY and self._is_running:
            next(update_client)             
            if counter % 100 == 0:
                log.info("Waiting for remote status READY")
            time.sleep(0.1)
            counter += 1

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

        if self._is_running:
            return
        
        if not auto_close:
            counter = 0
            while client.training_state in State.idle_states and self._is_running:
                next(update_client)                                     
                if counter % 20 == 0:
                    log.info("Idle. Graph count: " + str(len(self._graphs)))                     
                time.sleep(0.5)
                
        log.info("Exiting run internal with state " + str(client.training_state))
        return client.training_state
    
    def _on_receive_graph(self, graph):
        self._graphs.append(graph)        

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

        log.info('Userland error:\n' + error.format())
        if self._issue_handler is not None:
            self._issue_handler.put_error(error.format())
        self._is_running = False                
        
    @property
    def graphs(self) -> List[Graph]:
        copy_graph = self._graphs.copy()
        self._graphs = []
        return copy_graph

    def close(self, wait_for_deployment=False):
        #if self._client is not None:
        #    self._client.send_event('on_stop')
        #    self._client.stop()
        
        if self._client is not None:
            log.info(f"Sent close command to training server")
            self._client.request_close()
            self._client.shutdown()
            self._client = None

            if wait_for_deployment:
                log.info("Waiting for deployment to shutdown...")
                if self._deployment_strategy.shutdown(timeout=240):
                    log.info("Deployment shut down!")
                else:
                    log.info("Deployment did not shut down!")                                        
        self._is_running = False


    #def stop(self):
    #    if self._client is not None:
    #        self._client.request_stop()        
        
    def pause(self):
        if self._client is not None:
            self._client.request_pause()
        else:
            log.warning("Requested pause but training client not set!!")

    def unpause(self):
        if self._client is not None:
            self._client.request_resume()
    
    def headlessOn(self):
        if self._client is not None:
            self._client.request_headless_activate()
        
    def headlessOff(self):
        if self._client is not None:
            self._client.request_headless_deactivate()

    def export(self, path: str, mode: str):
        log.debug(f"Export path: {path}, mode: {mode}, client: {self._client}")
        
        if self._client is not None:            
            self._client.request_export(path, mode)
        else:
            log.warning("Client is none. on_export not called!")

    def stop(self):
        if self._client is not None:
            self._client.request_stop()
            
    @property
    def is_running(self):
        return self._is_running

    @property
    def is_paused(self):
        return self._client is not None and self._client.training_state in State.paused_states
            
    @property
    def training_state(self):
        if self._client is not None:
            return self._client.training_state
        else:
            return None
        
        

    
