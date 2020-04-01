import time
import uuid
import pprint
import logging
import requests
import tempfile
import threading
import subprocess
import sentry_sdk
from typing import Dict, List, Callable
from abc import ABC, abstractmethod
from queue import Queue

from perceptilabs.issues import IssueHandler, UserlandError
from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.deployment import DeploymentPipe
from perceptilabs.core_new.api.mapping import ByteMap
from perceptilabs.core_new.communication.status import *


log = logging.getLogger(__name__)


class Core:
    def __init__(self, graph_builder: GraphBuilder, deployment_pipe: DeploymentPipe, issue_handler: IssueHandler=None):
        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._graphs = []
        self._issue_handler = issue_handler
        
        self._lock = threading.Lock()        
        self._is_running = threading.Event()
        self._is_running.clear()
        self._client = None
        
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

        from perceptilabs.core_new.layers.script import ScriptFactory
        self._script_factory = ScriptFactory()

        graph = self._graph_builder.build_from_spec(graph_spec)

        code, line_to_node_map = self._script_factory.make(graph, session_id)

        with open('training_script.py', 'wt') as f:
            f.write(code)
            f.flush()


        def fn_start():
            import importlib
            
            with open('training_script.py', 'rt') as f:            
                spec = importlib.util.spec_from_file_location("deployed_module", f.name)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.main()

        from multiprocessing import Process
        process = Process(target=fn_start) # Process > thread to avoid interference between TensorFlow instances.
        process.start()
        time.sleep(3) # Give it some time to start.. TODO: wait until shared memory is available, after that we can connect at will.


        from perceptilabs.core_new.communication import TrainingClient, State
        training_client = TrainingClient(
            6556, 6557,
            graph_builder=self._graph_builder
        )
        #import pdb; pdb.set_trace()

        training_client.connect()
        while training_client.remote_status == None:
            print("waiting for ready!!!")            
            time.sleep(0.1)
        
        training_client.request_start()
        while training_client.remote_status == State.READY:
            print("waiting for running!!!")
            time.sleep(0.1)

        if training_client.remote_status == State.RUNNING:
            log.info(f"Training client connected to server. Session id: {session_id}")
        else:
            raise RuntimeError(f"Expected status {State.RUNNING}, got {training_client.remote_status}!")


        counter = 0
        while training_client.remote_status in [State.RUNNING, State.PAUSED]:
            if counter % 30 == 0:
                log.info("Training running/paused. Graph count: " + str(len(self._graphs)))                
            self._graphs = training_client.graphs.copy()
            time.sleep(0.1)
            counter += 1

            
        if auto_stop:
            training_client.request_stop()            
                        
        counter = 0
        while training_client.remote_status == State.IDLE:
            if counter % 30 == 0:
                log.info("Idle. Graph count: " + str(len(self._graphs)))                     
            time.sleep(0.1)


        if training_client.remote_status == State.DONE:
            log.info("Done!: ")
        elif training_client.remote_status == None:
            log.info("Done, but with none! ")            
        elif training_client.remote_status == State.KILLED:
            log.info("Killed!!!")            
            

        training_client.stop()

        
        
    def _run_internal_(self, graph_spec: JsonNetwork, session_id: str=None, on_iterate: List[Callable]=None):        
        session_id = session_id or uuid.uuid4().hex
        log.info(f"Running core with session id {session_id}")

        config = self._deployment_pipe.get_session_config(session_id)
        log.debug(f"Session {session_id} config: {pprint.pformat(config)}")
        
        graph = self._graph_builder.build_from_spec(graph_spec)
        self._client = self._deployment_pipe.deploy(graph, session_id)

        line_to_node_map = self._deployment_pipe._line_to_node_map # TODO: inject script_factory to deployment pipe instead retrieving the map like this.

        log.info(f"Sending start command to deployed core with session id {session_id}")        
        self._client.send_event('on_start')
        
        while self._client.status in [STATUS_READY, STATUS_STARTED]:
            time.sleep(1.0)

        if self._client.status == STATUS_RUNNING:
            log.info(f"Deployed core with id {session_id} indicated status 'running'")
        else:
            raise RuntimeError(f"Expected deployed core status 'running', but got '{self._client.status}'")

        self._graphs = []

        counter = 0
        t_start = time.perf_counter()
        while self._client.status in [STATUS_RUNNING, STATUS_RUNNING_PAUSED] or (self._client.status == STATUS_IDLE and len(self._graphs) < self._client.snapshot_count):
            t0 = time.perf_counter()
            errors = self._client.pop_errors()

            if errors:
                self._handle_errors(errors, line_to_node_map)
                log.info('Breaking out of core main loop due to remote errors: ' + ', '.join(repr(e) for e, _ in errors))                
                break

            snapshots = self._client.pop_snapshots()

            total_size = 0
            new_graphs = []
            for snapshot, size in snapshots:
                graph = self._graph_builder.build_from_snapshot(snapshot)
                new_graphs.append(graph)                
                total_size += size

            with self._lock:
                self._graphs.extend(new_graphs)
 
            for f in on_iterate:
                f(counter, self)

            t1 = time.perf_counter()

            running_time = self._client.running_time
            produce_rate = round(self._client.snapshot_count / running_time, 3)
            consume_rate = round(len(self._graphs) / running_time, 3)
            avg_size = round(total_size/10**3/len(snapshots), 3) if len(snapshots) > 0 else 0.0

            log.info(
                f"Consumed {len(snapshots)} snapshots in {round(1000*(t1-t0), 3)} ms (mean size: {avg_size} KB). "
                f"Total consumed (produced): {len(self._graphs)} ({self._client.snapshot_count}). "
                f"Consumption (production) rate: {consume_rate} ({produce_rate}) per sec. "
            )
            counter += 1
            time.sleep(1)

    @property
    def is_paused(self):
        return self._client.status == STATUS_RUNNING_PAUSED

    def _handle_errors(self, errors: List, line_to_node_map):
        errors_repr = []
        for _, traceback_frames in errors:
            message = ''

            for frame in traceback_frames:
                node, true_lineno = line_to_node_map.get(frame.lineno, (None, None))

                if frame.filename == 'deploy.py' and node is not None:
                    message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}, ' + \
                               f'origin {node.layer_id}:{true_lineno} [{node.layer_type}]\n' +\
                               f'  {frame.line}\n'
                else:
                    message += f'File "{frame.filename}", line {frame.lineno}, in {frame.name}\n' + \
                               f'  {frame.line}\n'

            userland_error = UserlandError(node.layer_id, node.layer_type, frame.lineno, message)

            with sentry_sdk.push_scope() as scope:
                scope.set_tag('error-type', 'userland-error')
                scope.level = 'info'
                sentry_sdk.capture_message(userland_error.format())
            
            log.info('Userland error:\n' + userland_error.format())
            if self._issue_handler is not None:
                self._issue_handler.put_error(userland_error.format())          
            
    @property
    def graphs(self) -> List[Graph]:
        with self._lock:
            return self._graphs.copy()

    def stop(self):
        #if self._client is not None:
        #    self._client.send_event('on_stop')
        #    self._client.stop()
        #    log.info(f"Sent stop command to deployed core")                        
            
        self._is_running.clear()
        
    def pause(self):
        if self._client is not None:
            self._client.send_event('on_pause')

    def unpause(self):
        if self._client is not None:        
            self._client.send_event('on_resume')
    
    def headlessOn(self):
        if self._client is not None:
            self._client.send_event('on_headless_activate')

    def headlessOff(self):
        if self._client is not None:
            self._client.send_event('on_headless_deactivate')

    def export(self, path: str, mode: str):
        log.debug(f"Export path: {path}, mode: {mode}, client: {self._client}")
        
        if self._client is not None:        
            self._client.send_event('on_export', path=path, mode=mode)
        else:
            log.warning("Client is none. on_export not called!")

    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
