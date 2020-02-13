import zmq
import dill
import zlib
import json
import time
import urllib
import logging
import requests
import threading
from queue import Queue
from collections import namedtuple


log = logging.getLogger(__name__)


class ClientError(Exception):
    pass

class Client:
    MAX_SNAPSHOTS_PER_ITERATION = 10
    
    def __init__(self, hostname):
        self._hostname = hostname
        
        self._snapshot_queue = None

        self._snapshot_worker_thread = threading.Thread(target=self._snapshot_worker, daemon=True)
        self._snapshot_worker_thread.start()

    @property
    def status(self):
        with urllib.request.urlopen(self._hostname+"/") as url:
            buf = url.read().decode()
        dict_ = json.loads(buf)
        status = dict_['status']
        return status

    @property
    def running_time(self):
        with urllib.request.urlopen(self._hostname+"/") as url:
            buf = url.read().decode()
        dict_ = json.loads(buf)
        status = dict_['running_time']
        return status
    
    @property
    def snapshot_count(self):
        with urllib.request.urlopen(self._hostname+"/") as url:
            buf = url.read().decode()
        dict_ = json.loads(buf)
        count = dict_['snapshot_count']
        return int(count)
        

    def pop_snapshots(self):
        snapshots = []

        # Allow max 100 snapshots per pop for a smoother frontend rendering.
        while not self._snapshot_queue.empty():
            snap, size = self._snapshot_queue.get()
            snapshots.append((snap, size))
        return snapshots

    def _send_event(self, type_, **kwargs):
        json_dict = {'type': type_, **kwargs}
        requests.post(self._hostname+"/command", json=json_dict)                
        
    def start(self):
        self._send_event('on_start')    

    def stop(self):
        self._is_running.clear()
    
    def _snapshot_worker(self):
        self._snapshot_queue = Queue()
        self._is_running = threading.Event()
        self._is_running.set()        

        ctx = zmq.Context()                
        socket = ctx.socket(zmq.SUB)
        socket.connect('tcp://localhost:7171')
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
            exc = dill.loads(body)
            log.error("Received exception from deployed core: " + repr(exc))
        elif topic == b'log_message':
            message = dill.loads(body)
            log.info("Deployed core: " + message)
        else:
            log.warning("Received message over unknown topic" + str(topic))
