import zmq
import dill
import zlib
import json
import time
import queue
import urllib
import logging
import requests
import threading
import traceback
from queue import Queue
from collections import namedtuple


from perceptilabs.core_new.utils import YieldLevel
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

    allowed_transitions = set((
        (INITIALIZING, READY),
        (INITIALIZING, STOPPED),        
        (READY, RUNNING),
        (READY, STOPPED),
        (STARTED, RUNNING),
        (RUNNING, RUNNING),
        (PAUSED, RUNNING),
        (PAUSED, STOPPED),                
        (RUNNING, STOPPED),
        (RUNNING, IDLE),
        (STOPPED, DONE),
        (IDLE, DONE),        
    ))
    
    def __init__(self):
        self._state = self.INITIALIZING
        self._lock = threading.Lock()

    @property
    def value(self):
        return self._state

    def transition(self, new_state):
        with self._lock: 
            if (self._state, new_state) in self.allowed_transitions:
                self._state = new_state
            else:
                raise StateTransitionError(f"Cannot transition from '{self._state}' to '{new_state}'")

            
class TrainingServer:    
    def __init__(self, port_pub_sub, port_push_pull, graph, snapshot_builder=None):
        self._is_running = threading.Event()
        self._is_running.clear()
        
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull
        
        self._graph = graph
        self._state = None
        
        self._snapshot_builder = snapshot_builder
        self._serialization_fn = serialize

    def start(self, threaded=True):
        self._is_running.set()
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

    def _worker_func(self):
        event_queue = queue.Queue()
        
        self._zmq_server = ZmqServer(
            f'tcp://*:{self._port_pub_sub}',
            f'tcp://*:{self._port_push_pull}',            
        )
        self._zmq_server.start()

        training_state = State()
        handlers = {
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

        print("enter main loop")
        
        while self._is_running.is_set() and step_result is not sentinel:
            self._zmq_client.process_messages()

            if training_state.value == State.RUNNING:
                try:
                    step_result = next(training_step, sentinel)
                except Exception as e:
                    self._send_userland_error(e)
                    
            if step_result is YieldLevel.SNAPSHOT:
                self._send_snapshot(self._graph)

            if step_result is sentinel:
                training_state.transition(State.IDLE)
                self._send_state(training_state.value)

        self._zmq_client.stop()
        self._zmq_server.stop()
        
    def _handle_raw_event(self, raw_event, graph, training_state):
        event_dict = deserialize(raw_event)
        event_type = event_dict['type']
        event_data = event_dict.get('data', None)

        print("handle raw event" + str(event_dict))
        if event_type == 'on_connect':
            self._send_state(training_state.value)
        if event_type == 'on_request_start':
            training_state.transition(State.RUNNING)
            self._send_state(training_state.value)
        
    def _send_snapshot(self, graph):
        self._snapshot_builder.build(graph)
        value = self._serialization_fn(snapshot)
        self._zmq_client.push(b'snapshots', value)

    def _send_userland_error(self, exception):
        tb_list = traceback.extract_tb(exception.__traceback__)
        value = self._serialization_fn((exception, tb_list))
        self._zmq_client.push(b'exception', value)

    def _send_state(self, state):
        value = serialize(state)
        self._zmq_client.push(b'state', value)

    def send_log_message(self):
        pass

    def stop(self):
        self._is_running.clear()
        self._worker_thread.join()
        
class TrainingClient:
    def __init__(self, port_pub_sub, port_push_pull, graph_builder=None):
        self._is_running = threading.Event()
        self._is_running.clear()        

        
        self._graph_builder = graph_builder
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull

        self._remote_status = None
        
    @property
    def remote_status(self):
        return self._remote_status

    def _on_receive_status(self, value):
        self._remote_status = deserialize(value)
        print('recv STATUS' , self._remote_status)    

    def _worker_func(self):
        handlers = {
            #b'snapshots': lambda client, value: 0
            #b'log_message': lambda client, value: 0
            #b'exception': lambda client, value: 0
            b'state': lambda client, key, value: self._on_receive_status(value)
        }
        
        self._zmq_client = ZmqClient(
            f'tcp://localhost:{self._port_pub_sub}',
            f'tcp://localhost:{self._port_push_pull}',            
            handlers
        )
        self._zmq_client.start()
        
        while self._is_running.is_set():
            self._zmq_client.process_messages()            
            time.sleep(0.1)
            
        self._zmq_client.stop()

    def connect(self):
        self._is_running.set()   
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

        raw_event = serialize({'type': 'on_connect'})
        self._zmq_client.push(b'event', raw_event)        

    def request_start(self):
        raw_event = serialize({'type': 'on_request_start'})
        self._zmq_client.push(b'event', raw_event)

    def stop(self):
        self._is_running.clear()
        self._worker_thread.join()


class Client:
    MAX_FLASK_FAILURES = 10
    MAX_SNAPSHOTS_PER_ITERATION = 10
    
    def __init__(self, config):
        self._flask_address = config['addr_flask']
        self._zmq_address = config['addr_zmq']        
        
        self._snapshot_queue = None
        self._error_queue = None     

        self._is_running = threading.Event()
        self._is_running.set()   

        self._snapshot_worker_thread = threading.Thread(target=self._snapshot_worker, daemon=True)
        self._snapshot_worker_thread.start()

        self._flask_worker_thread = threading.Thread(target=self._flask_worker, daemon=True)
        self._flask_worker_thread.start()

        self._flask_status = dict()

    @property
    def status(self):
        status = self._flask_status.get('status')
        return status

    @property
    def running_time(self):
        status = self._flask_status.get('running_time')
        return status
    
    @property
    def snapshot_count(self):
        count = self._flask_status.get('snapshot_count')
        return int(count)

    def pop_snapshots(self):
        snapshots = []

        while not self._snapshot_queue.empty():
            snap, size = self._snapshot_queue.get()
            snapshots.append((snap, size))
        return snapshots

    def pop_errors(self):
        errors = []

        while not self._error_queue.empty():
            error = self._error_queue.get()
            errors.append(error)
        return errors    

    def send_event(self, type_, **kwargs):
        json_dict = {'type': type_, **kwargs}
        requests.post(self._flask_address+"/command", json=json_dict)                
        
    def stop(self):
        self._is_running.clear()

    def _flask_worker(self):
        def process():
            with urllib.request.urlopen(self._flask_address+"/") as url:
                buf = url.read().decode()
                dict_ = json.loads(buf)
                self._flask_status = dict_.copy()

        failures = []
        while self._is_running.is_set():
            try:
                process()
            except Exception as e:
                failures.append(e)                
            else:
                failures = []
            finally:
                time.sleep(0.5)
                
            if len(failures) >= self.MAX_FLASK_FAILURES:
                log.error(f"Flask worker failed {failures} times in a row: {', '.join(failures)}. Stopping communication client!")
                self.stop()


                
    def _snapshot_worker(self):
        self._error_queue = Queue()        
        self._snapshot_queue = Queue()  

        ctx = zmq.Context()                
        socket = ctx.socket(zmq.SUB)
        socket.connect(self._zmq_address)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        
        while self._is_running.is_set():
            items = dict(poller.poll(timeout=0.1))
            if socket in items:
                topic, body = socket.recv_multipart()                
                self._handle_message(topic, body)

    def _handle_message(self, topic, body):
        if topic == b'snapshots':
            snapshot = dill.loads(body)
            size = len(body)
            self._snapshot_queue.put((snapshot, size))
        elif topic == b'exception':
            error = dill.loads(body)
            #log.error("Received exception from deployed core: " + repr(exc))

            self._error_queue.put(error)
            #raise RemoteError("Received exception from deployed core" + repr(exc), exc)            
        elif topic == b'log_message':
            message = dill.loads(body)
            log.info("Deployed core: " + message)
        else:
            log.warning("Received message over unknown topic" + str(topic))

