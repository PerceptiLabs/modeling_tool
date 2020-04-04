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
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
#from perceptilabs.core_new.communication.zmq import Client as ZmqClient, Server as ZmqServer
from perceptilabs.core_new.communication.zmq2 import ZmqClient, ZmqServer, ConnectionLost
from perceptilabs.core_new.communication.task_executor import TaskExecutor, TaskError, TaskTimeout


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
    TRAINING_PAUSED = 'training-paused'
    TRAINING_PAUSED_HEADLESS = 'training-paused-headless'    
    TRAINING_RUNNING = 'training-running'
    TRAINING_RUNNING_HEADLESS = 'training-running-headless'    
    TRAINING_COMPLETED = 'training-completed'
    TRAINING_STOPPED = 'training-stopped'
    TRAINING_TIMEOUT = 'training-timeout'
    TRAINING_FAILED = 'training-failed'
    FINALIZING = 'finalizing'

    idle_states = set((READY, TRAINING_PAUSED, TRAINING_COMPLETED, TRAINING_STOPPED))
    exit_states = set((FINALIZING, TRAINING_TIMEOUT, TRAINING_FAILED))
    
    allowed_transitions = set((
        (INITIALIZING, READY),
        (READY, TRAINING_RUNNING),
        (READY, TRAINING_STOPPED),        
        (TRAINING_RUNNING, TRAINING_TIMEOUT),
        (TRAINING_RUNNING, TRAINING_FAILED),
        (TRAINING_RUNNING, TRAINING_COMPLETED),
        (TRAINING_RUNNING, TRAINING_PAUSED),
        (TRAINING_RUNNING, TRAINING_STOPPED),
        (TRAINING_RUNNING, TRAINING_RUNNING_HEADLESS),
        (TRAINING_RUNNING_HEADLESS, TRAINING_TIMEOUT),
        (TRAINING_RUNNING_HEADLESS, TRAINING_FAILED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_COMPLETED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_PAUSED_HEADLESS),
        (TRAINING_RUNNING_HEADLESS, TRAINING_STOPPED),
        (TRAINING_RUNNING_HEADLESS, TRAINING_RUNNING),                                
        (TRAINING_PAUSED, TRAINING_RUNNING),
        (TRAINING_PAUSED, TRAINING_STOPPED),
        (TRAINING_PAUSED, TRAINING_PAUSED_HEADLESS),
        (TRAINING_PAUSED_HEADLESS, TRAINING_RUNNING_HEADLESS),
        (TRAINING_PAUSED_HEADLESS, TRAINING_PAUSED),                        
        (READY, FINALIZING)
    ))
    
    def __init__(self, on_transition=None):
        self._state = self.INITIALIZING
        self._lock = threading.Lock()
        self._on_transition = on_transition

    @property
    def value(self):
        return self._state

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
    
    def transition(self, new_state):
        if new_state is None:
            return        
        if self._state == new_state:
            return
        
        with self._lock: 
            if (self._state, new_state) in self.allowed_transitions:
                self._state = new_state
            else:
                raise StateTransitionError(f"Cannot transition from '{self._state}' to '{new_state}'")
            if self._on_transition:
                self._on_transition(new_state)
                
    @classmethod
    def visualize(cls):
        import matplotlib.pyplot as plt
        import networkx as nx
        graph = nx.DiGraph()
        
        x = list(cls.allowed_transitions)
        graph.add_edges_from(x)
        pos = nx.shell_layout(graph)
        #pos = nx.circular_layout(graph)    
        nx.draw(graph, pos, with_labels=True)
        plt.show()
        
    
        

class TrainingServer:
    def __init__(self, port_pub_sub, port_push_pull, graph, snapshot_builder=None, step_timeout=15):
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull

        self._snapshot_builder = snapshot_builder        
        self._step_timeout = step_timeout
        self._graph = graph

    def run(self):
        step_generator = self.run_step()
        for _ in step_generator:
            pass

    def run_step(self):
        zmq = self._zmq = ZmqServer(
            f'tcp://*:{self._port_pub_sub}',
            f'tcp://*:{self._port_push_pull}',            
        )
        zmq.start()

        def on_transition(new_state):
            log.info(f"Entered new state {new_state}")
            self._send_message(zmq, 'state', new_state)            

        state = State(on_transition=on_transition)
        
        training_iterator = self._graph.run()
        training_sentinel = object()
        training_step_result = None
        
        def training_step():
            return next(training_iterator, training_sentinel)
        
        task_executor = TaskExecutor()
        main_step_times = collections.deque(maxlen=1)
        train_step_times = collections.deque(maxlen=1)        
        
        state.transition(State.READY)
        log.info("Entering main-loop [TrainingServer]")
        t1 = t2 = 0
        while state.value not in State.exit_states:
            t0 = time.perf_counter()
            new_state = self._process_messages(zmq, state)
            state.transition(new_state)

            if state.value == State.TRAINING_RUNNING:
                t1 = time.perf_counter()                
                new_state = self._process_training(
                    zmq,
                    training_step,
                    training_sentinel,
                    task_executor
                )
                t2 = time.perf_counter()
                state.transition(new_state)                
            elif state.value in State.idle_states:
                self._send_message(zmq, 'state', state.value)                            
                time.sleep(1.0)
            t3 = time.perf_counter()
            
            main_step_times.append(t3 - t0)
            train_step_times.append(t2 - t1)

            import numpy as np
            print(np.average(main_step_times))
            print(np.average(train_step_times))
            
            yield

        zmq.stop()
        log.info(f"Leaving main-loop. Exit state: {state.value} [TrainingServer]")
        return state.value

    def shutdown(self):
        self._zmq.stop()

    def _process_training(self, zmq, training_step, sentinel, task_executor):
        new_state = None
        try:
            training_step_result = task_executor.run(
                training_step,
                timeout=self._step_timeout
            )
            print("rtrrr result", training_step_result, sentinel)
        except TaskTimeout as e:
            new_state = State.TRAINING_TIMEOUT
            self._send_userland_timeout()                    
        except TaskError as e:
            new_state = State.TRAINING_FAILED            
            self._send_userland_error(e.__cause__)
        else:
            if training_step_result is sentinel:
                new_state = State.TRAINING_COMPLETED
            elif training_step_result is YieldLevel.SNAPSHOT:
                self._send_graph(zmq, self._graph)
        finally:
            return new_state

    def _send_userland_timeout(self):
        self._send_message(self._zmq, 'userland-timeout')        
    
    def _send_userland_error(self, exception):
        tb_frames = traceback.extract_tb(exception.__traceback__)
        data = {'exception': exception, 'traceback_frames': tb_frames}
        self._send_message(self._zmq, 'userland-error', data)                
                          
    def _process_messages(self, zmq, state):
        for message in zmq.get_messages():
            self._process_message(message, state)

    def _process_message(self, raw_message, state):
        message = deserialize(raw_message)
        print('MESSAGE', message)
        message_key = message['key']
        message_value = message['value']

        new_state = None
        if message_key == 'on_request_start':
            state.transition(State.TRAINING_RUNNING)
        elif message_key == 'on_request_stop':
            self._call_userland_method(
                self._graph.on_stop,
                state,
                success_state=State.TRAINING_STOPPED
            )
        elif message_key == 'on_request_export':
            self._call_userland_method(
                self._graph.on_export,
                state,
                args=(message_value['path'], message_value['mode'])
            )
        elif message_key == 'on_request_headless_activate':
            if state.value == State.TRAINING_RUNNING:            
                self._call_userland_method(
                    self._graph.on_headless_activate,
                    state,
                    success_state=State.TRAINING_RUNNING_HEADLESS
                )
            elif state.value == State.TRAINING_PAUSED:
                self._call_userland_method(
                    self._graph.on_headless_activate,
                    state,
                    success_state=State.TRAINING_PAUSED_HEADLESS
                )
            else:
                raise StateTransitionError()
        elif message_key == 'on_request_headless_deactivate':
            if state.value == State.TRAINING_RUNNING_HEADLESS:            
                self._call_userland_method(
                    self._graph.on_headless_deactivate,
                    state,
                    success_state=State.TRAINING_RUNNING
                )
            elif state.value == State.TRAINING_PAUSED_HEADLESS:
                self._call_userland_method(
                    self._graph.on_headless_deactivate,
                    state,
                    success_state=State.TRAINING_PAUSED
                )
            else:
                raise StateTransitionError()                
        elif message_key == 'on_request_pause':
            if state.value == State.TRAINING_RUNNING:
                state.transition(State.TRAINING_PAUSED)
            elif state.value == State.TRAINING_RUNNING_HEADLESS:
                state.transition(State.TRAINING_PAUSED_HEADLESS)
            else:
                raise StateTransitionError()                
        elif message_key == 'on_request_resume':
            if state.value == State.TRAINING_PAUSED:            
                state.transition(State.TRAINING_RUNNING)
            elif state.value == State.TRAINING_PAUSED_HEADLESS:            
                state.transition(State.TRAINING_RUNNING_HEADLESS)
            else:
                raise StateTransitionError()                
        else:
            #raise RuntimeError(f"Unknown event key '{message_key}'")
            log.warning(f"Unknown event key '{message_key}'")            
            pass # TODO: hmm, snapshots will go here too.... Block them in ZMQ server somehow?
        
        return new_state

    def _call_userland_method(self, method, state, args=None, kwargs=None, success_state=None):
        args = args or ()
        kwargs = kwargs or {}
        try:
            method(*args, **kwargs)
        except Exception as e:
            log.exception('Error in userland method. Setting state to ' + str(State.TRAINING_FAILED))
            state.transition(State.TRAINING_FAILED)                              
            new_state = State.TRAINING_FAILED
        else:
            new_state = success_state
        finally:
            state.transition(new_state)
        
    def _send_message(self, zmq, key, value=None):
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        zmq.send_message(message)

    def _send_graph(self, zmq, graph):
        if self._snapshot_builder is not None:
            snapshot = self._snapshot_builder.build(graph)
            self._send_message(zmq, 'graph', snapshot)
    

class TrainingClient:
    def __init__(self, port_pub_sub, port_push_pull, graph_builder=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=20):
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull
        self._on_log_message = on_log_message
        self._on_userland_error = on_userland_error
        self._on_server_timeout = on_server_timeout
        self._server_timeout = server_timeout
        self._on_receive_graph = on_receive_graph
        self._graph_builder
        
        self._training_state = None
    
    def run_step(self):
        zmq = self._zmq = ZmqClient(
            f'tcp://localhost:{self._port_pub_sub}',
            f'tcp://localhost:{self._port_push_pull}',
            server_timeout=self._server_timeout
        )
        zmq.connect()

        while True:
            try:
                self._process_messages(zmq)
            except ConnectionLost:
                if self._on_server_timeout:
                    self._on_server_timeout()
                log.exception("No vital signs from training server..!")            
            yield

    def _process_messages(self, zmq):
        raw_messages = zmq.get_messages()
        for raw_message in raw_messages:
            message = deserialize(raw_message)
            message_key = message['key']
            message_value = message['value']
            self._process_message(message_key, message_value)

    def _process_message(self, key, value):
        if key == 'state':
            self._training_state = value
        elif key == 'log-message':
            if self._on_log_message:
                self._on_log_message(value['message'])
        elif key == 'userland-timeout':
            if self._on_userland_timeout:
                self._on_userland_timeout()
        elif key == 'userland-error':
            if self._on_userland_error:
                self._on_userland_error(value['exception'], value['traceback_list'])
        elif key == 'graph':
            if self._on_receive_graph and self._graph_builder:
                graph = self._graph_builder.build_from_snapshot(value)                
                self._on_receive_graph(graph)
        else:
            log.warning(f"Unknown message key {key}")

    def shutdown(self):
        self._zmq.stop()

    def _send_message(self, key, value=None):
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        self._zmq.send_message(message)
        
    def request_start(self):
        self._send_message('on_request_start')

    def request_pause(self):
        self._send_message('on_request_pause')

    def request_resume(self):
        self._send_message('on_request_resume')
        
    @property
    def training_state(self):
        return self._training_state        
        
'''            
class TrainingServer0:    
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
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

        counter = 0
        while not self._is_running.is_set():
            if counter % 100 == 0:
                log.info("Waiting for worker thread to initialize... [TrainingServer]")            
            time.sleep(0.1)
            counter += 1
            
        while block and self._is_running.is_set():
            time.sleep(1)
        
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

        def step_task():
            return next(training_step, sentinel)

        log.info("Entering worker loop [TrainingServer]")

        task_executor = TaskExecutor()
        
        counter = 0
        self._is_running.set()
        while self._is_running.is_set() and training_state.value != State.DONE:
            if counter % 100 == 0:
                log.info(f"Worker training loop iteration {counter}. Status: {training_state} [TrainingServer]")
            self._zmq_client.process_messages()

            if training_state.value == State.RUNNING:
                try:
                    self._step_start = time.time()
                    step_result = task_executor.run(step_task, timeout=self._max_step_time)
                except TaskTimeout:
                    self._send_killed()
                    training_state.transition(State.DONE)
                    log.exception("Userland timeout on iteration. Setting status to done and sending killed signal.")
                    break
                except TaskError as e:
                    self._send_userland_error(e)
                    training_state.transition(State.DONE)
                    log.exception("Userland error on iteration. Setting status to done and sending error.")
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
        #self._timeout_thread.join()

            
class TrainingClient0:
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

'''
if __name__ == "__main__":
    State.visualize()
