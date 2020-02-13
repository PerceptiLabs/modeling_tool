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


class Client:
    MAX_SNAPSHOTS_PER_ITERATION = 10
    
    def __init__(self, hostname):
        self._hostname = hostname
        
        self._snapshot_queue = None
        self._snapshots_fetched = 0

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
        self._snapshots_fetched = 0
        self._is_running = threading.Event()
        self._is_running.set()        


        ctx = zmq.Context()                
        socket = ctx.socket(zmq.SUB)
        socket.connect('tcp://localhost:7171')
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        

        while self._is_running.is_set():
            count = self._fetch_snapshots(poller, socket)

            if count == 0:
                time.sleep(1.0)

    def _fetch_snapshots(self, poller, socket):
        count = 0

        items = dict(poller.poll(timeout=0.1))

        if socket in items:
            topic, body = socket.recv_multipart()

            #print(body)
            
            #body = zlib.decompress(body)
            snapshot = dill.loads(body)
            size = len(body)
            
            self._snapshot_queue.put((snapshot, size))
            self._snapshots_fetched += 1
            count += 1

        return count
            
    def _fetch_snapshots_old(self):
        try:
            snapshot_count = self.snapshot_count
        except:
            return 0
            
        diff = snapshot_count - self._snapshots_fetched

        count = 0
        for idx in range(self._snapshots_fetched, self._snapshots_fetched + diff):
            try:
                with urllib.request.urlopen(self._hostname + f"/snapshot?index={idx}") as url:
                    buf = url.read()
                    
                hex_str = buf.decode()
                buf = bytes.fromhex(hex_str)
                buf = zlib.decompress(buf)

                size = len(buf)
                snapshot = dill.loads(buf)
            except Exception as e:
                log.exception("Error when fetching snapshots!")
                return count
            else:
                self._snapshot_queue.put((snapshot, size))
                self._snapshots_fetched += 1
                count += 1

        return count
