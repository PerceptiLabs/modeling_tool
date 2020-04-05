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
from perceptilabs.core_new.communication.zmq import ZmqClient, ZmqServer, ConnectionLost
from perceptilabs.core_new.communication.state import State, StateTransitionError
from perceptilabs.core_new.communication.task_executor import TaskExecutor, TaskError, TaskTimeout


log = logging.getLogger(__name__)
    

class TrainingClient:
    def __init__(self, port_pub_sub, port_push_pull, graph_builder=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=20):
        self._port_pub_sub = port_pub_sub
        self._port_push_pull = port_push_pull
        self._on_log_message = on_log_message
        self._on_userland_error = on_userland_error
        self._on_userland_timeout = on_userland_timeout
        self._on_server_timeout = on_server_timeout
        self._server_timeout = server_timeout
        self._on_receive_graph = on_receive_graph
        self._graph_builder = graph_builder
        
        self._training_state = None
    
    def run_stepwise(self):
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
                log.error("No vital signs from training server..!")                            
                if self._on_server_timeout:
                    self._on_server_timeout()
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
            log.info("Userland timeout")
            if self._on_userland_timeout:
                self._on_userland_timeout()
        elif key == 'userland-error':
            log.info("Userland error " + repr(value['exception']))            
            if self._on_userland_error:
                self._on_userland_error(value['exception'], value['traceback_frames'])
        elif key == 'graph':
            if self._on_receive_graph and self._graph_builder:
                graph = self._graph_builder.build_from_snapshot(value)                
                self._on_receive_graph(graph)
        else:
            log.warning(f"Unknown message key {key} [TrainingClient]")

    def shutdown(self):
        self._zmq.stop()

    def _send_message(self, key, value=None):
        message_dict = {'key': key, 'value': value or ''}
        message = serialize(message_dict)
        self._zmq.send_message(message)
        
    def request_start(self):
        self._send_message('on_request_start')

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

