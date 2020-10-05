import zlib
import uuid
import json
import time
import queue
import ctypes
import psutil
import urllib
import logging
import requests
import traceback
import collections
from queue import Queue



from perceptilabs.issues import traceback_from_exception
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.core_new.utils import YieldLevel, TracebackFrame
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.core_new.communication.state import State, StateTransitionError


logger = logging.getLogger(APPLICATION_LOGGER)


def is_tf_op_error(exception):
    """ Checks whether an exception implements tf.errors.OpError 

    Workaround for retrieving operation errors from errors raised in sess.run. 
    """
    
    import tensorflow as tf
    return isinstance(exception, tf.errors.OpError)


def extract_tf_op_traceback_frames(exception):
    """ Takes a tf.errors.OpError 

    Workaround for retrieving operation errors from errors raised in sess.run. 
    """
    original_op = exception.op # The first one is always not None
    while original_op is not None:
        op_tb = original_op.traceback
        original_op = original_op._original_op

    frames = [
        traceback.FrameSummary(lineno=tuple_[1], name=tuple_[2], filename=tuple_[0], line=tuple_[3])
        for tuple_ in op_tb
    ]
    return frames


class TrainingServer:
    def __init__(self, producer_generic, producer_snapshots, consumer, graph_builder, layer_classes, edges, connections, mode = 'training', snapshot_builder=None, userland_timeout=15, ping_interval=3, max_time_run=None, userland_logger=None):
        self._producer_generic = producer_generic
        self._producer_snapshots = producer_snapshots
        self._consumer = consumer

        self._snapshot_builder = snapshot_builder        
        self._userland_timeout = userland_timeout
        self._graph_builder = graph_builder
        self._layer_classes = layer_classes
        self._edges = edges
        self._connections = connections
        self._closing = False
        self._max_time_run = max_time_run
        self._mode = mode

        if userland_logger:
            self._handle_userland_logs(userland_logger)
        
    def run(self, auto_start=False):

            t0 = time.perf_counter()
            update_client = self.run_stepwise(auto_start=auto_start)
            for counter, _ in enumerate(update_client):
                if counter % 100 == 0:
                    logger.debug(f"Running step {counter}")
                if self._closing:
                    logger.info(f"Server closing. Leaving run loop {counter}")
                    break
                if self._max_time_run is not None and time.perf_counter() - t0 >= self._max_time_run:
                    logger.info(f"Exceeded run method max time. Leaving run loop {counter}")
                    break

    def run_stepwise(self, auto_start=False):
        self._consumer.start()                        
        self._producer_generic.start()
        self._producer_snapshots.start()
        
        state = State(on_transition=self._on_state_transition)

        try:
            self._graph = self._build_graph()            
        except Exception as e:
            self._send_userland_error(e)
            if self._mode == 'training':            
                state.transition(State.TRAINING_FAILED)
            elif self._mode == 'testing':
                state.transition(State.TESTING_FAILED)
            return
        
        if self._mode == 'training':
            yield from self.run_stepwise_training(state, auto_start)
        elif self._mode == 'testing':
            yield from self.run_stepwise_testing(state, auto_start)
        elif self._mode == 'exporting':
            yield from self.run_stepwise_exporting(state, auto_start)
            
        
        return state.value

    def run_stepwise_training(self, state, auto_start=False):
        training_iterator = self._graph.run(self._mode)
        training_sentinel = object()
        training_step_result = None

        def training_step():
            return next(training_iterator, training_sentinel)   
        
        state.transition(State.READY)
        if auto_start:
            state.transition(State.TRAINING_RUNNING) 
        else:
            self._send_key_value('state', state.value)           
        
        logger.info("Entering main-loop [TrainingServer]")
        counter = 0
        t_start = time.perf_counter()
        sent_training_ended = False
        session_info = collections.defaultdict(list)
        
        while state.value not in State.exit_states:
            initial_state = state.value
            t_training_step = t_send_snapshot = t_process_messages = 0 # Defaults
            
            t0 = time.perf_counter()
            new_state = self._process_messages(state)
            t_process_messages = time.perf_counter() - t0
            
            state.transition(new_state)
            if state.value in State.running_states:
                new_state = None
                try:
                    t = time.perf_counter()
                    training_step_result = training_step()
                except Exception as e:
                    t_training_step = time.perf_counter() - t
                    logger.info("Training step raised an error: " + traceback_from_exception(e))

                    new_state = State.TRAINING_FAILED
                    self._send_userland_error(e)
                else: 
                    t_training_step = time.perf_counter() - t
                    if training_step_result is training_sentinel:
                        new_state = State.TRAINING_COMPLETED
                    elif training_step_result is YieldLevel.SNAPSHOT:
                        t = time.perf_counter()
                        self._send_graph(self._graph)
                        t_send_snapshot = time.perf_counter() - t

                state.transition(new_state)
                
            elif state.value in State.idle_states:                
                if counter % 5 == 0:
                    #logger.info(f"In idle state '{state.value}'")                                
                    self._send_key_value('state', state.value)
                time.sleep(1.0)
                
            elif state.value not in State.exit_states:
                raise RuntimeError(f"Unexpected state: {state}")

            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            t_cycle = time.perf_counter() - t0

            n_decimals = 6 #microseconds precision         
            session_info['cycle_state_initial'].append(initial_state)
            session_info['cycle_state_final'].append(state.value)
            session_info['cycle_time_process_messages'].append(round(t_process_messages, n_decimals))
            session_info['cycle_time_training_step'].append(round(t_training_step, n_decimals))
            session_info['cycle_time_send_snapshot'].append(round(t_send_snapshot, n_decimals))
            session_info['cycle_time_total'].append(round(t_cycle, n_decimals))
            session_info['cycle_mem_phys_available'].append(int(virtual_memory.available))
            session_info['cycle_mem_swap_free'].append(int(swap_memory.free))
            
            if not sent_training_ended and state.value in State.ended_states:
                t_total = time.perf_counter() - t_start
                session_info = dict(session_info)
                session_info['time_total'] = t_total
                session_info['mem_phys_total'] = int(virtual_memory.total)
                session_info['mem_swap_total'] = int(swap_memory.total)                
                self._send_training_ended(session_info, state.value)
                sent_training_ended = True
            counter += 1
            yield

        self.shutdown(state)
        return state

    def run_stepwise_testing(self, state, auto_start=False):
        testing_iterator = self._graph.run(self._mode)
        testing_sentinel = object()
        testing_step_result = None

        def testing_step():
            return next(testing_iterator, testing_sentinel)
        
        state.transition(State.READY)
        if auto_start:
            state.transition(State.TESTING_RUNNING)
        else:
            self._send_key_value('state', state.value)            
        
        logger.info("Entering main-loop testing [TrainingServer]")
        counter = 0
        snapshot_count = 0
        sent_testing_ended = False
        t0 = time.time()

        while state.value not in State.exit_states:
            initial_state = state.value
            self._process_messages(state)
            if state.value in State.running_states:
                t0 = time.time()
                new_state = None
                try:
                    testing_step_result = testing_step()
                    snapshot_count += 1
                    new_state = State.TESTING_PAUSED
                except Exception as e:
                    logger.info("testing step raised an error: " + traceback_from_exception(e))
                    new_state = State.TESTING_FAILED
                    self._send_userland_error(e)
                else: 
                    if testing_step_result is testing_sentinel:
                        new_state = State.TESTING_STOPPED
                    elif testing_step_result is YieldLevel.SNAPSHOT:
                        self._send_graph(self._graph)

                state.transition(new_state)
                
            elif state.value in State.idle_states:                
                if counter % 5 == 0:
                    #logger.info(f"In idle state '{state.value}'")                                
                    self._send_key_value('state', state.value)
                if time.time() - t0 > 120:
                    state.transition(state.TESTING_STOPPED)
                time.sleep(1.0)
                
            elif state.value not in State.exit_states:
                raise RuntimeError(f"Unexpected state: {state}")

            
            
            if not sent_testing_ended and state.value in State.ended_states:
                
                sent_testing_ended = True
            counter += 1
            yield

        self.shutdown(state)
        return state

    def run_stepwise_exporting(self, state, auto_start=False):
        
        state.transition(State.READY)
        state.transition(State.TRAINING_RUNNING) 
        self._graph.init_layer(self._mode)
        
        while state.value not in State.exit_states:
            self._process_messages(state)
            yield

        self.shutdown(state)
        return state
    
    def shutdown(self, state=None):
        self._closing = True
        if state:
            state.transition(State.CLOSING)
        
        self._producer_generic.stop()
        self._producer_snapshots.stop()
        self._consumer.stop()

        logger.info("TrainingServer consumers closed.")

    def _build_graph(self):
        layers = {}
        for layer_id, layer_class in self._layer_classes.items():
            layers[layer_id] = layer_class()        
        
        graph = self._graph_builder.build_from_layers_and_edges(
            layers, self._edges, connections=self._connections
        )
        return graph
        

    def _advance_training(self, training_step, sentinel):
        """Take a training step, check for userland errors, send snapshot if possible"""
        
        new_state = None
        try:
            training_step_result = training_step()
        except Exception as e:
            logger.info("Training step raised an error: " + repr(e))            
            new_state = State.TRAINING_FAILED
            self._send_userland_error(e)
        else:
            if training_step_result is sentinel:
                new_state = State.TRAINING_COMPLETED
            elif training_step_result is YieldLevel.SNAPSHOT:
                self._send_graph(self._graph)
        finally:
            return new_state        
        
    def _advance_testing(self, testing_step, sentinel):
        """Take a testing step, check for userland errors, send snapshot if possible"""
        
        new_state = None
        try:
            testing_step_result = testing_step()
        except Exception as e:
            logger.info("Training step raised an error: " + repr(e))            
            new_state = State.TESTING_FAILED
            self._send_userland_error(e)
        else:
            if testing_step_result is sentinel:
                new_state = State.TESTING_STOPPED
            elif testing_step_result is YieldLevel.SNAPSHOT:
                self._send_graph(self._graph)
        finally:
            return new_state        

    def _on_state_transition(self, new_state):
        self._send_key_value('state', new_state)
        logger.info(f"Transitioned to state '{new_state}'")

    def _send_userland_timeout(self):
        self._send_key_value('userland-timeout')        
    
    def _send_userland_error(self, exception):
        if is_tf_op_error(exception):
            # TensorFlow raises errors on sess.run(), but we want errors from the operation itself            
            frames = extract_tf_op_traceback_frames(exception)
        else:
            frames = traceback.extract_tb(exception.__traceback__)            
        
        tb_frames = [
            TracebackFrame(frame.lineno, frame.name, frame.filename, frame.line)
            for frame in frames
        ]
            
        data = {
            'exception': exception.message if hasattr(exception, 'message') else repr(exception),
            'traceback_frames': tb_frames
        }
        self._send_key_value('userland-error', data)

    def _send_training_ended(self, session_info, state_value):
        self._closed_by_server = True        
        self._send_key_value(
            'training-ended', {'session_info': session_info, 'end_state': state_value}
        )   
        
    def _process_messages(self, state):
        messages = self._consumer.get_messages(per_message_timeout=0.000001)
        for message in messages:
            self._process_message(message, state)

    def _process_message(self, raw_message, state):
        message = deserialize(raw_message)
        message_key = message['key']
        message_value = message['value']
        new_state = None

        if message_key == 'on_request_start':
            if self._mode in ['training', 'exporting'] :
                state.transition(State.TRAINING_RUNNING)
            elif self._mode =='testing':
                state.transition(State.TESTING_RUNNING)

        if message_key == 'on_request_close':
            state.transition(State.CLOSING)

        elif message_key == 'on_request_stop':
            if self._mode in ['training', 'exporting'] :
                success_state = State.TRAINING_STOPPED
            elif self._mode =='testing':
                success_state = State.TESTING_STOPPED
            self._call_userland_method(
                self._graph.on_stop,
                state,
                success_state=success_state
            )

        elif message_key == 'on_request_export':
            print('export called')
            self._call_userland_method(
                self._graph.on_export,
                state,
                success_state=State.TRAINING_COMPLETED,
                args=(message_value['path'], message_value['mode'])
            )

        elif message_key == 'on_advance_testing':
            if state.value == State.TESTING_PAUSED:
                state.transition(State.TESTING_RUNNING)

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
                raise StateTransitionError(f"Couldn't transition from {state.value}")

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
                raise StateTransitionError(f"Couldn't transition from {state.value}")

        elif message_key == 'on_request_pause':
            if state.value == State.TRAINING_RUNNING:
                state.transition(State.TRAINING_PAUSED)
            elif state.value == State.TRAINING_RUNNING_HEADLESS:
                state.transition(State.TRAINING_PAUSED_HEADLESS)
            else:
                raise StateTransitionError(f"Couldn't transition from {state.value}") 

        elif message_key == 'on_request_resume':
            if state.value == State.TRAINING_PAUSED:            
                state.transition(State.TRAINING_RUNNING)
            elif state.value == State.TRAINING_PAUSED_HEADLESS:            
                state.transition(State.TRAINING_RUNNING_HEADLESS)
            else:
                raise StateTransitionError(f"Couldn't transition from {state.value}")                                
        else:
            #raise RuntimeError(f"Unknown event key '{message_key}'")
            #logger.warning(f"Unknown event key '{message_key}'")            
            pass # TODO: hmm, snapshots will go here too.... Block them in ZMQ server somehow?
        
        return new_state

    def _call_userland_method(self, method, state, args=None, kwargs=None, success_state=None):
        args = args or ()
        kwargs = kwargs or {}
        try:
            method(*args, **kwargs)
        except Exception as e:
            logger.info("Userland method raised an error: " + repr(e))            
            self._send_userland_error(e)
            state.transition(State.TRAINING_FAILED)            
        else:
            state.transition(success_state)

    def _send_key_value(self, key, value=None, producer=None):
        producer = producer or self._producer_generic
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        producer.send(message)

    def _send_graph(self, graph):
        if self._snapshot_builder is not None:            
            snapshot = self._snapshot_builder.build(graph)
            self._send_key_value('graph', value=snapshot, producer=self._producer_snapshots)

    def _handle_userland_logs(self, userland_logger):
        def send_key_value(key, value):
            self._send_key_value(key, value)                

        class MyHandler(logging.Handler):
            def emit(self, record):
                dict_ = {'message': self.format(record), 'level': record.levelname}
                send_key_value('log-message', value=dict_)
        
        userland_logger.addHandler(MyHandler())
