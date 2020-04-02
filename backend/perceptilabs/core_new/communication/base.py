import zmq
import dill
import zlib
import uuid
import json
import time
import queue
import ctypes
import urllib
import logging
import requests
import threading
import traceback
import collections
from queue import Queue



from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.utils import KillableThread
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.core_new.communication.zmq import Client as ZmqClient, Server as ZmqServer


log = logging.getLogger(__name__)


class RemoteError(Exception):
    def __init__(self, message, original_exception):
        super().__init__(message)
        self.original_exception = original_exception

        
class StateTransitionError(Exception):
    pass


class State:
    INITIALIZING = 'initializing'
    READY = 'ready'
    STARTED = 'started'
    STOPPED = 'stopped'
    WAITING = 'waiting'
    RUNNING = 'running'
    PAUSED = 'paused'
    IDLE = 'idle'
    DONE = 'done'    
    STOPPED = 'stopped'    

    # (FROM_STATE, TO_STATE)
    allowed_transitions = set((
        (INITIALIZING, READY),
        (READY, RUNNING),
        (READY, DONE),
        (RUNNING, DONE),        
        (RUNNING, PAUSED),
        (PAUSED, RUNNING),
        (PAUSED, DONE),
        (RUNNING, IDLE),
        (IDLE, DONE),        
    ))
    
    def __init__(self):
        self._state = self.INITIALIZING
        self._lock = threading.Lock()

    @property
    def value(self):
        return self._state

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
    
    def transition(self, new_state):
        if self._state == new_state:
            return
        
        with self._lock: 
            if (self._state, new_state) in self.allowed_transitions:
                self._state = new_state
            else:
                raise StateTransitionError(f"Cannot transition from '{self._state}' to '{new_state}'")

            
class TrainingServer:    
    def __init__(self, port_pub_sub, port_push_pull, graph, snapshot_builder=None, max_step_time=15):
        self._is_running = threading.Event()
        self._is_running.clear()
        
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull
        
        self._graph = graph
        self._state = None
        self._step_start = None
        self._max_step_time = max_step_time
        
        self._snapshot_builder = snapshot_builder
        self._serialization_fn = serialize

    def start(self, block=False):
        self._worker_thread = KillableThread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

        counter = 0
        while not self._is_running.is_set():
            if counter % 100 == 0:
                log.info("Waiting for worker thread to initialize... [TrainingServer]")            
            time.sleep(0.1)
            counter += 1
            
        self._timeout_thread = threading.Thread(target=self._timeout_func, daemon=True)
        self._timeout_thread.start()

        while block and self._is_running.is_set():
            time.sleep(1)
        
    def _timeout_func(self):
        while self._is_running.is_set():
            if self._step_start is not None:
                step_time = time.time() - self._step_start
                if step_time > self._max_step_time:
                    log.info(f"Training step time has been running for {step_time}s, exceeding limit of {self._max_step_time}s. Killing worker thread. [TrainingServer]")
                    self._worker_thread.kill()
                    
                    log.info("Sending message 'killed'")                    
                    self._send_killed()                    
                    
                    log.info("Stopping everything...")
                    self._is_running.clear()                        
                    #self._zmq_client.stop()
                    #self._zmq_server.stop()                        
                    break
            time.sleep(0.5)
        log.info("Leaving timeout function")

    def _worker_func(self):
        log.info("Entering worker func [TrainingServer]")
        event_queue = queue.Queue()

        log.info(f"Binding to publisher socket {self._port_pub_sub} and pull socket {self._port_push_pull} [TrainingServer]")
        self._zmq_server = ZmqServer(
            f'tcp://*:{self._port_pub_sub}',
            f'tcp://*:{self._port_push_pull}',            
        )
        self._zmq_server.start()

        training_state = State()
        handlers = {
            b'ping': lambda client, key, value: self._handle_ping(value),
            b'event': lambda client, key, value: self._handle_raw_event(value, self._graph, training_state)
        }
        self._zmq_client = ZmqClient(
            f'tcp://localhost:{self._port_pub_sub}',
            f'tcp://localhost:{self._port_push_pull}',            
            handlers
        )
        self._zmq_client.start()

        training_state.transition(State.READY)
        self._send_state(training_state.value)

        sentinel = object()
        training_step = self._graph.run()
        step_result = None

        log.info("Entering worker loop [TrainingServer]")

        counter = 0
        self._is_running.set()
        while self._is_running.is_set() and training_state.value != State.DONE:
            if counter % 100 == 0:
                log.info(f"Worker training loop iteration {counter}. Status: {training_state} [TrainingServer]")
            self._zmq_client.process_messages()

            if training_state.value == State.RUNNING:
                try:
                    self._step_start = time.time()
                    step_result = next(training_step, sentinel)
                except Exception as e:
                    self._send_userland_error(e)
                    log.exception("Userland error on iteration. Setting status to done.")
                    training_state.transition(State.DONE)
                finally:
                    self._step_start = None                    
            else:
                step_result = None
                    
            if step_result is sentinel and training_state.value == State.RUNNING:
                training_state.transition(State.IDLE)
                self._send_state(training_state.value)
                
            if step_result is YieldLevel.SNAPSHOT:
                self._send_graph(self._graph)
                    
            if training_state.value != State.RUNNING:
                time.sleep(0.01)
                
            counter += 1

        training_state.transition(State.DONE)            
        self._send_state(training_state.value)

        #log.info("Closing ZeroMQ client [TrainingServer]")                
        #self._zmq_client.stop()
        #log.info("Closing ZeroMQ server [TrainingServer]")                        
        #self._zmq_server.stop()
        self._is_running.clear()

    def _call_userland_method(self, training_state, method_fn, *args, **kwargs):
        try:
            method_fn(*args, **kwargs)
        except Exception as e:
            self._send_userland_error(e)
            log.exception("Userland error on iteration. Setting status to done.")
            training_state.transition(State.DONE)
            return False
        return True
            
    def _handle_raw_event(self, raw_event, graph, training_state):
        event_dict = deserialize(raw_event)
        event_type = event_dict['type']

        log.info(f"Handling raw event '{event_type}'")                        
        if event_type == 'on_connect':
            self._send_state(training_state.value)
        elif event_type == 'on_request_start':
            training_state.transition(State.RUNNING)
            self._send_state(training_state.value)
        elif event_type == 'on_request_stop':
            if training_state.value == State.RUNNING:
                self._call_userland_method(training_state, graph.active_training_layer.layer.on_stop)
            training_state.transition(State.DONE)
            self._send_state(training_state.value)
        elif event_type == 'on_request_export':
            self._call_userland_method(
                training_state,
                graph.active_training_layer.layer.on_export,
                event_dict['path'], event_dict['mode']
            )            
        elif event_type == 'on_request_pause':
            training_state.transition(State.PAUSED)
            self._send_state(training_state.value)
        elif event_type == 'on_request_resume':
            training_state.transition(State.RUNNING)
            self._send_state(training_state.value)
        else:
            log.warning(f"Unknown event type {event_type}")

    def _handle_ping(self, id_):
        self._zmq_client.push(b'pong', id_)
            
    def _send_graph(self, graph):
        snapshot = self._snapshot_builder.build(graph)
        value = serialize(snapshot)
        self._zmq_client.push(b'graph', value)

    def _send_userland_error(self, exception):
        tb_list = traceback.extract_tb(exception.__traceback__)
        value = serialize({'exception': exception, 'traceback_list': tb_list})
        self._zmq_client.push(b'userland-error', value)
        
    def _send_state(self, state):
        value = serialize(state)
        self._zmq_client.push(b'state', value)

    def send_log_message(self, message):
        value = serialize(message)
        self._zmq_client.push(b'log-message', value)

    def _send_killed(self):
        value = serialize('')
        self._zmq_client.push(b'killed', value)        

    def stop(self):
        log.info("Stopping [TrainingServer]")        
        if self._is_running.is_set():
            self._is_running.clear()

        self._zmq_client.stop()
        self._zmq_server.stop()                        
            
        self._worker_thread.join()
        self._timeout_thread.join()

            
class TrainingClient:
    def __init__(self, port_pub_sub, port_push_pull, graph_builder=None, on_userland_error=None, on_log_message=None, on_server_killed=None, on_server_timeout=None, max_response_time=20):
        self._is_running = threading.Event()
        self._is_running.clear()        

        self._graph_builder = graph_builder
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull

        self._on_userland_error = on_userland_error
        self._on_log_message = on_log_message
        self._remote_status = None
        self._ping_sent = {}
        self._ping_list = collections.deque([], maxlen=10)
        self._max_response_time = max_response_time
        self._on_server_timeout = on_server_timeout
        self._on_server_killed = on_server_killed
        
        self._graphs = []
        
    @property
    def remote_status(self):
        if self._is_running.is_set():
            return self._remote_status
        else:
            return None

    @property
    def graphs(self):
        return self._graphs.copy()

    def _on_receive_state(self, value):
        self._remote_status = deserialize(value)
        log.info(f"Received state {self._remote_status} [TrainingClient]")

    def _on_receive_graph(self, value):
        #log.info(f"Received graph [TrainingClient]")        
        if self._graph_builder:
            snapshot = deserialize(value)
            graph = self._graph_builder.build_from_snapshot(snapshot)            
            self._graphs.append(graph)
        else:
            log.warning("Received graph but graph builder is not set!")

    def _on_receive_userland_error(self, value):
        error_dict = deserialize(value)
        exception = error_dict['exception']
        tb_list = error_dict['traceback_list']
        log.info(f"Received userland error. {repr(exception)}")

        if self._on_userland_error is not None:
            self._on_userland_error(exception, tb_list)

    def _on_receive_log_message(self, value):
        message = deserialize(value)
        if self._on_log_message is not None:
            self._on_log_message(message)

    def _on_receive_pong(self, value):
        id_ = deserialize(value)
        diff = time.time() - self._ping_sent[id_]
        self._ping_list.append(diff)
        del self._ping_sent[id_]

    def _on_receive_killed(self):
        log.info("Received 'killed' message")
        if self._on_server_killed is not None:
            self._on_server_killed()
        self._is_running.clear()        

    def ping(self):
        ping_list = list(self._ping_list)
        if len(ping_list) > 0:
            return sum(ping_list)/len(ping_list)
        else:
            return None

    def _server_not_responding(self):
        t1 = time.time()
        ping_sent = self._ping_sent.copy()
        return any(t1 - t0 > self._max_response_time for t0 in ping_sent.values())
        
    def _worker_func(self):
        log.info("Entering worker func [TrainingClient]")                
        handlers = {
            b'log-message': lambda client, value: self._on_receive_log_message(value),
            b'userland-error': lambda client, key, value: self._on_receive_userland_error(value),
            b'graph': lambda client, key, value: self._on_receive_graph(value),
            b'state': lambda client, key, value: self._on_receive_state(value),
            b'pong': lambda client, key, value: self._on_receive_pong(value),
            b'killed': lambda client, key, value: self._on_receive_killed()                        
        }

        log.info(f"Binding to subscriber socket {self._port_pub_sub} and push socket {self._port_push_pull} [TrainingClient]")        
        self._zmq_client = ZmqClient(
            f'tcp://localhost:{self._port_pub_sub}',
            f'tcp://localhost:{self._port_push_pull}',            
            handlers
        )
        self._zmq_client.start()

        log.info("Entering worker loop [TrainingClient]")        
        counter = 0
        self._is_running.set()
        while self._is_running.is_set():
            if counter % 100 == 0:
                log.info(f"Worker loop iteration {counter} [TrainingClient]")                                      
            self._zmq_client.process_messages()

            if counter % 10 == 0:
                self._send_ping()

            if self._server_not_responding():
                log.info("Server not responding. Leaving worker loop.")
                self._is_running.clear()
                if self._on_server_timeout is not None:
                    self._on_server_timeout()
                    
            time.sleep(0.01)
            counter += 1
            
    def connect(self):
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

        counter = 0
        while not self._is_running.is_set():
            if counter % 100 == 0:
                log.info("Waiting for worker thread to initialize... [TrainingClient]")            
            time.sleep(0.1)
            counter += 1

        raw_event = serialize({'type': 'on_connect'})
        self._zmq_client.push(b'event', raw_event)

    def _send_ping(self):
        id_ = uuid.uuid4().hex
        value = serialize(id_)
        self._zmq_client.push(b'ping', value)
        self._ping_sent[id_] = time.time()

    def request_start(self):
        raw_event = serialize({'type': 'on_request_start'})
        self._zmq_client.push(b'event', raw_event)

    def request_stop(self):
        raw_event = serialize({'type': 'on_request_stop'})
        self._zmq_client.push(b'event', raw_event)

    def request_export(self, path, mode):
        raw_event = serialize({'type': 'on_request_export', 'path': path, 'mode': mode})
        self._zmq_client.push(b'event', raw_event)
        
    def request_pause(self):
        raw_event = serialize({'type': 'on_request_pause'})
        self._zmq_client.push(b'event', raw_event)

    def request_resume(self):
        raw_event = serialize({'type': 'on_request_resume'})
        self._zmq_client.push(b'event', raw_event)        
        
    def stop(self):
        log.info("Stopping [TrainingClient]")
        
        if self._is_running.is_set():
            self._is_running.clear()

        self._zmq_client.stop()
        self._worker_thread.join()

    @property
    def is_running(self):
        return self._is_running.is_set()


