# Requirements:
# 
#     (1) send any event downstream
#     (2) receive any event upstream
#     (3) events are processed on main-thread

import zmq
import queue
import threading
from typing import Dict, Callable


class Server:
    def __init__(self, publisher_address: str, pull_address: str):
        self._pub_addr = publisher_address
        self._pull_addr = pull_address
        self._worker_thread = None
        self._is_running = threading.Event()
        self._is_running.clear()

    def _worker_func(self):
        ctx = zmq.Context()        
        publisher_socket = ctx.socket(zmq.PUB)
        pull_socket = ctx.socket(zmq.PULL)
        
        publisher_socket.bind(self._pub_addr)        
        pull_socket.bind(self._pull_addr)

        poller = zmq.Poller()
        poller.register(pull_socket, zmq.POLLIN)        

        while self._is_running.is_set():
            items = dict(poller.poll(timeout=0.1))

            if pull_socket in items:
                key, value = pull_socket.recv_multipart()
                publisher_socket.send_multipart([key, value])
            
    def start(self):
        self._is_running.set()        
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

    def stop(self):
        if self._is_running.is_set():
            self._is_running.clear()
            self._worker_thread.join()

    @property
    def is_running(self):
        return self._is_running.is_set()


class Client:
    def __init__(self, subscriber_address: str, push_address: str, handlers: Dict[bytes, Callable]):
        self._sub_addr = subscriber_address
        self._push_addr = push_address

        self._out_queue = queue.Queue()
        self._in_queue = queue.Queue()

        self._handlers = handlers or dict()

        self._worker_thread = None
        self._is_running = threading.Event()
        self._is_running.clear()

    def push(self, key: bytes, value: bytes):
        self._out_queue.put((key, value))

    def process_messages(self):
        while not self._in_queue.empty():
            key, value = self._in_queue.get()

            if key in self._handlers:
                handler = self._handlers[key]
                handler(self, key, value)                    
            else:
                pass # Warning?

    def _worker_func(self):
        ctx = zmq.Context()

        self._messages_sent = 0
        self._messages_received = 0
        
        subscriber_socket = ctx.socket(zmq.SUB)
        subscriber_socket.linger = 0
        for key in self._handlers.keys():
            subscriber_socket.setsockopt(zmq.SUBSCRIBE, key)
        subscriber_socket.connect(self._sub_addr)

        push_socket = ctx.socket(zmq.PUSH)
        push_socket.linger = 0
        push_socket.connect(self._push_addr)
        
        poller = zmq.Poller()
        poller.register(subscriber_socket, zmq.POLLIN)
        
        while self._is_running.is_set():
            items = dict(poller.poll(timeout=0.1))
            
            if subscriber_socket in items:
                key, value = subscriber_socket.recv_multipart()
                self._messages_received += 1                
                self._in_queue.put((key, value))

            if not self._out_queue.empty():
                key, value = self._out_queue.get()
                push_socket.send_multipart([key, value])
                self._messages_sent += 1


    def _init_socket(self, ctx, zmq_type, address, options=None):
        socket = ctx.socket(zmq_type)
        socket.linger = 0

        options = options or []
        for opt in options:
            socket.setsockopt_string(opt[0], opt[1])

        socket.connect(address)
        return socket

    def start(self):
        self._is_running.set()        
        self._worker_thread = threading.Thread(target=self._worker_func, daemon=True)
        self._worker_thread.start()

    def stop(self):
        if self._is_running.is_set():
            self._is_running.clear()
            self._worker_thread.join()

    @property
    def is_running(self):
        return self._is_running.is_set()

    @property
    def messages_sent(self):
        return self._messages_sent

    @property
    def messages_received(self):
        return self._messages_received
    
