import zmq
import dill
import zlib
import json
import time
import queue
import ctypes
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
    KILLED = 'killed'

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
        
        #(INITIALIZING, STOPPED),        
        #(STARTED, RUNNING),

        #(PAUSED, RUNNING),
        #(PAUSED, STOPPED),                
        #(RUNNING, STOPPED),
        #(RUNNING, IDLE),
        #(STOPPED, DONE),
        #(IDLE, DONE),        
    ))
    
    def __init__(self):
        self._state = self.INITIALIZING
        self._lock = threading.Lock()

    @property
    def value(self):
        return self._state

    def transition(self, new_state):
        if self._state == new_state:
            return
        
        with self._lock: 
            if (self._state, new_state) in self.allowed_transitions:
                self._state = new_state
            else:
                raise StateTransitionError(f"Cannot transition from '{self._state}' to '{new_state}'")

            
class TrainingServer:    
    def __init__(self, port_pub_sub, port_push_pull, graph, snapshot_builder=None, max_step_time=60):
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

    def start(self, threaded=True):
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

        counter = 0
        while not self._is_running.is_set():
            if counter % 100 == 0:
                log.info("Waiting for worker thread to initialize... [TrainingServer]")            
            time.sleep(0.1)
            counter += 1
            
        self._timeout_thread = threading.Thread(target=self._timeout_func, args=(self._worker_thread.ident,), daemon=True)
        self._timeout_thread.start()

    def _timeout_func(self, worker_thread_id):
        while self._is_running.is_set():

            if self._step_start is not None:
                step_time = time.time() - self._step_start
                if step_time > self._max_step_time:
                    log.info(f"Training step time took {step_time}s, exceeding limit {self._max_step_time}s")
                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(worker_thread_id, ctypes.py_object(SystemExit))

                    time.sleep(1)
                    if res == 0:
                        self._send_state(State.KILLED)
                        time.sleep(1) # Ensure it's sent..

                        self._is_running.clear()                        
                        self._zmq_client.stop()
                        self._zmq_server.stop()                        
                    else:
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(worker_thread_id, 0) 
                        raise RuntimeError("Failed to kill worker thread!")
                    
                    break
                    
                    log.info('res'+str(res))
            time.sleep(1)

    def _worker_func(self):
        log.info("Entering worker func [TrainingServer]")
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

        log.info("Entering worker loop [TrainingServer]")

        counter = 0
        self._is_running.set()
        while self._is_running.is_set() and training_state.value is not State.DONE:
            if counter % 1000 == 0:
                log.info(f"Worker loop iteration {counter} [TrainingServer]")                                
            self._zmq_client.process_messages()

            if training_state.value == State.RUNNING:
                try:
                    self._step_start = time.time()
                    step_result = next(training_step, sentinel)
                except Exception as e:
                    self._send_userland_error(e)
                    log.exception("Userland error. Setting status to done.")
                    training_state.transition(State.DONE)
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

        self._send_state(training_state.value)                    
        log.info("Closing ZeroMQ client [TrainingServer]")                
        self._zmq_client.stop()
        log.info("Closing ZeroMQ server [TrainingServer]")                        
        self._zmq_server.stop()
        
    def _handle_raw_event(self, raw_event, graph, training_state):
        event_dict = deserialize(raw_event)
        event_type = event_dict['type']
        event_data = event_dict.get('data', None)

        log.info(f"Handling raw event '{event_type}'")                        
        if event_type == 'on_connect':
            self._send_state(training_state.value)
        if event_type == 'on_request_start':
            training_state.transition(State.RUNNING)
            self._send_state(training_state.value)
        elif event_type == 'on_request_stop':
            training_state.transition(State.DONE)
            self._send_state(training_state.value)
        elif event_type == 'on_request_pause':
            training_state.transition(State.PAUSED)
            self._send_state(training_state.value)
        elif event_type == 'on_request_resume':
            training_state.transition(State.RUNNING)
            self._send_state(training_state.value)


            
    def _send_graph(self, graph):
        snapshot = self._snapshot_builder.build(graph)
        value = serialize(snapshot)
        self._zmq_client.push(b'graph', value)

    def _send_userland_error(self, exception):
        tb_list = traceback.extract_tb(exception.__traceback__)
        value = serialize({'exception': exception, 'traceback_list': tb_list})
        self._zmq_client.push(b'userland-error', value)
        
    def _send_userland_error(self, exception):
        tb_list = traceback.extract_tb(exception.__traceback__)
        value = serialize({'exception': exception, 'traceback_list': tb_list})
        self._zmq_client.push(b'userland-error', value)
        
    def _send_state(self, state):
        value = serialize(state)
        self._zmq_client.push(b'state', value)

    def send_log_message(self):
        pass

    def stop(self):
        if self._is_running.is_set():
            log.info("Stopping [TrainingServer]")
            self._is_running.clear()
            self._worker_thread.join()

            
class TrainingClient:
    def __init__(self, port_pub_sub, port_push_pull, graph_builder=None, userland_error_handler=None):
        self._is_running = threading.Event()
        self._is_running.clear()        

        self._graph_builder = graph_builder
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull

        self._userland_error_handler = userland_error_handler
        self._remote_status = None

        self._graphs = []
        
    @property
    def remote_status(self):
        return self._remote_status

    @property
    def graphs(self):
        return self._graphs

    def _on_receive_state(self, value):
        self._remote_status = deserialize(value)
        log.info(f"Received state {self._remote_status} [TrainingClient]")

    def _on_receive_graph(self, value):
        log.info(f"Received graph [TrainingClient]")        
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

        if self._userland_error_handler is not None:
            self._userland_error_handler(exception, tb_list)

    def _worker_func(self):
        log.info("Entering worker func [TrainingClient]")                
        handlers = {
            #b'log_message': lambda client, value: 0
            b'userland-error': lambda client, key, value: self._on_receive_userland_error(value),
            b'graph': lambda client, key, value: self._on_receive_graph(value),
            b'state': lambda client, key, value: self._on_receive_state(value)
        }
        
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
            if counter % 1000 == 0:
                log.info(f"Worker loop iteration {counter} [TrainingClient]")                                      
            self._zmq_client.process_messages()            
            time.sleep(0.1)
            counter += 1
            
        self._zmq_client.stop()

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

    def request_start(self):
        raw_event = serialize({'type': 'on_request_start'})
        self._zmq_client.push(b'event', raw_event)

    def request_stop(self):
        raw_event = serialize({'type': 'on_request_stop'})
        self._zmq_client.push(b'event', raw_event)

    def request_pause(self):
        raw_event = serialize({'type': 'on_request_pause'})
        self._zmq_client.push(b'event', raw_event)

    def request_resume(self):
        raw_event = serialize({'type': 'on_request_resume'})
        self._zmq_client.push(b'event', raw_event)        
        
    def stop(self):
        if self._is_running.is_set():
            log.info("Stopping [TrainingClient]")            
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

