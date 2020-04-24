import zlib
import uuid
import json
import time
import queue
import ctypes
import urllib
import logging
import requests
import traceback
import collections
from queue import Queue



from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.core_new.communication.state import State, StateTransitionError
from perceptilabs.core_new.communication.task_executor import TaskExecutor, TaskError, TaskTimeout


log = logging.getLogger(__name__)
        

class TrainingServer:
    def __init__(self, producer_key_value, producer_snapshots, consumer, graph, snapshot_builder=None, userland_timeout=15, ping_interval=3, max_time_run=None):
        self._producer_key_value = producer_key_value
        self._producer_snapshots = producer_snapshots
        self._consumer = consumer

        self._snapshot_builder = snapshot_builder        
        self._userland_timeout = userland_timeout
        self._graph = graph
        self._closing = False
        self._max_time_run = max_time_run

    def run(self):
        t0 = time.perf_counter()
        update_client = self.run_stepwise()
        for counter, _ in enumerate(update_client):
            if counter % 100 == 0:
                log.info(f"Running step {counter}")
            if self._closing:
                log.info(f"Server closing. Leaving run loop {counter}")
                break
            if self._max_time_run is not None and time.perf_counter() - t0 >= self._max_time_run:
                log.info(f"Exceeded run method max time. Leaving run loop {counter}")
                break

    def run_stepwise(self):
        self._consumer.start()                        
        self._producer_key_value.start()
        self._producer_snapshots.start()
        
        def on_transition(new_state):
            log.info(f"Entered new state {new_state}")
            self._send_key_value('state', new_state)
            
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
        counter = 0
        while state.value not in State.exit_states:
            t0 = time.perf_counter()
            new_state = self._process_messages(state)
            state.transition(new_state)
            
            if state.value in State.running_states:
                t1 = time.perf_counter()                
                new_state = self._process_training(
                    training_step,
                    training_sentinel,
                    task_executor
                )
                t2 = time.perf_counter()
                state.transition(new_state)                
            elif state.value in State.idle_states:
                if counter % 10 == 0:
                    log.info(f"In idle state '{state.value}'")                
                
                self._send_key_value('state', state.value)
                time.sleep(1.0)
            elif state.value not in State.exit_states:
                raise RuntimeError(f"Unexpected state: {state}")
            
            t3 = time.perf_counter()            
            main_step_times.append(t3 - t0)
            train_step_times.append(t2 - t1)

            #import numpy as np
            #print(np.average(main_step_times))
            #print(np.average(train_step_times))
            counter += 1
            yield

        self._closing = True
        self.shutdown()
        return state.value

    def shutdown(self):
        self._producer_key_value.stop()
        self._producer_snapshots.stop()
        self._consumer.stop()

    def _process_training(self, training_step, sentinel, task_executor):
        new_state = None
        try:
            training_step_result = task_executor.run(
                training_step,
                timeout=self._userland_timeout
            )
        except TaskTimeout as e:
            log.info("Training step timed out!")
            new_state = State.TRAINING_TIMEOUT
            self._send_userland_timeout()                    
        except TaskError as e:
            log.info("Training step raised an error!")            
            new_state = State.TRAINING_FAILED
            self._send_userland_error(e.__cause__)
        else:
            if training_step_result is sentinel:
                new_state = State.TRAINING_COMPLETED
            elif training_step_result is YieldLevel.SNAPSHOT:
                self._send_graph(self._graph)
        finally:
            return new_state

    def _send_userland_timeout(self):
        self._send_key_value('userland-timeout')        
    
    def _send_userland_error(self, exception):
        tb_frames = traceback.extract_tb(exception.__traceback__)
        data = {'exception': exception, 'traceback_frames': tb_frames}
        self._send_key_value('userland-error', data)                
        
    def _process_messages(self, state):
        messages = self._consumer.get_messages()
        for message in messages:
            self._process_message(message, state)

    def _process_message(self, raw_message, state):
        message = deserialize(raw_message)
        #print('TRN SRVR PROCESSING MESSAGE', message)
        message_key = message['key']
        message_value = message['value']
        
        new_state = None
        if message_key == 'on_request_start':
            state.transition(State.TRAINING_RUNNING)
        if message_key == 'on_request_close':
            state.transition(State.CLOSING)
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
            #log.warning(f"Unknown event key '{message_key}'")            
            pass # TODO: hmm, snapshots will go here too.... Block them in ZMQ server somehow?
        
        return new_state

    def _call_userland_method(self, method, state, args=None, kwargs=None, success_state=None):
        args = args or ()
        kwargs = kwargs or {}
        try:
            method(*args, **kwargs)
        except Exception as e:
            log.exception('Error in userland method. Setting state to ' + str(State.TRAINING_FAILED))
            self._send_userland_error(e.__cause__)            
            state.transition(State.TRAINING_FAILED)                              
        else:
            state.transition(success_state)
        
    def _send_key_value(self, key, value=None):
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        self._producer_key_value.send(message)

    def _send_graph(self, graph):
        if self._snapshot_builder is not None:
            snapshot = self._snapshot_builder.build(graph)
            self._producer_snapshots.send(snapshot)
