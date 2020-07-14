import zmq
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


from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.core_new.communication.zmq import ZmqClient, ZmqServer, ConnectionLost
from perceptilabs.core_new.communication.state import State, StateTransitionError
from perceptilabs.core_new.communication.task_executor import TaskExecutor, TaskError, TaskTimeout


logger = logging.getLogger(APPLICATION_LOGGER)
    

class TrainingClient:
    def __init__(self, producer, consumer, graph_builder=None, on_state_changed=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=20, on_training_ended=None):
        self._producer = producer
        self._consumer = consumer
        self._on_log_message = on_log_message
        self._on_userland_error = on_userland_error
        self._on_userland_timeout = on_userland_timeout
        self._on_server_timeout = on_server_timeout
        self._server_timeout = server_timeout
        self._on_receive_graph = on_receive_graph
        self._on_state_changed = on_state_changed
        self._on_training_ended = on_training_ended
        self._graph_builder = graph_builder
        
        self._out_queue = queue.Queue()
        
        self._training_state = None
    
    def run_stepwise(self):
        self._consumer.start()
        self._producer.start()

        self._running = True
        self._t_last_message = time.time()
        while self._running:
            self._process_incoming_messages()                            
            self._process_outgoing_messages()                    
            yield

    def _process_incoming_messages(self):
        raw_messages = self._consumer.get_messages(per_message_timeout=0.001)
        for raw_message in raw_messages:
            message = deserialize(raw_message)
            message_key = message['key']
            message_value = message['value']
            self._process_incoming_key_value(message_key, message_value)

        if len(raw_messages) > 0:
            self._t_last_message = time.time()
        elif time.time() - self._t_last_message > self._server_timeout:
            logger.error(f"No vital signs from the training server within the last {self._server_timeout} seconds.")
            if self._on_server_timeout:
                self._on_server_timeout()
            
            time.sleep(0.1)

                
    def _process_incoming_key_value(self, key, value):
        if key == 'state':
            self._training_state = value
            if self._on_state_changed:
                self._on_state_changed(value)
        if key == 'training-ended':
            if self._on_training_ended:
                self._on_training_ended(value)
        elif key == 'log-message':
            if self._on_log_message:
                self._on_log_message(value['message'])
        elif key == 'userland-timeout':
            logger.info("Userland timeout")
            if self._on_userland_timeout:
                self._on_userland_timeout()
        elif key == 'userland-error':
            logger.info("Userland error " + repr(value['exception']))            
            if self._on_userland_error:
                self._on_userland_error(value['exception'], value['traceback_frames'])
        elif key == 'graph':
            if self._on_receive_graph and self._graph_builder:
                graph = self._graph_builder.build_from_snapshot(value)                
                self._on_receive_graph(graph)
        else:
            logger.warning(f"Unknown message key {key} [TrainingClient]")

    def _process_outgoing_messages(self):
        while not self._out_queue.empty():
            message = self._out_queue.get()
            self._producer.send(message)            
            
    def shutdown(self):
        self._running = False
        self._process_outgoing_messages()
        self._producer.stop()
        self._consumer.stop()        

    def _send_message(self, key, value=None):
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        self._out_queue.put(message)
        
    def request_start(self):
        self._send_message('on_request_start')

    def request_stop(self):
        self._send_message('on_request_stop')
        
    def request_close(self):
        self._send_message('on_request_close')
        
    def request_pause(self):
        self._send_message('on_request_pause')

    def request_resume(self):
        self._send_message('on_request_resume')

    def request_headless_activate(self):
        self._send_message('on_request_headless_activate')        

    def request_headless_deactivate(self):
        self._send_message('on_request_headless_deactivate')        
        
    def request_export(self, path, mode):
        self._send_message('on_request_export', {'path': path, 'mode': mode})
        
    @property
    def training_state(self):
        return self._training_state        

