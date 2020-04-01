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


class RemoteError(Exception):
    def __init__(self, message, original_exception):
        super().__init__(message)
        self.original_exception = original_exception
        

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
