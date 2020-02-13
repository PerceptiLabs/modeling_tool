import dill
import zlib
import json
import time
import urllib
import requests
import threading
from queue import Queue
from collections import namedtuple


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
    def snapshot_count(self):
        with urllib.request.urlopen(self._hostname+"/") as url:
            buf = url.read().decode()
        dict_ = json.loads(buf)
        count = dict_['n_snapshots']
        return int(count)
        

    def pop_snapshots(self):
        snapshots = []

        # Allow max 100 snapshots per pop for a smoother frontend rendering.
        while not self._snapshot_queue.empty() and len(snapshots) < 100:
            s = self._snapshot_queue.get()
            snapshots.append(s)
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
        
        while self._is_running.is_set():
            try:
                self._fetch_snapshots()
            except Exception as e:
                print('exxxxxccccpt', repr(e))
                
            time.sleep(0.5)
            
    def _fetch_snapshots(self):
        snapshots = []
        with urllib.request.urlopen(self._hostname+"/snapshot_count") as url:
            buf = url.read().decode()

        snapshot_count = int(buf)

        sz_tot_buf = 0
        sz_decompr = 0

        diff = snapshot_count - self._snapshots_fetched
        for idx in range(self._snapshots_fetched, self._snapshots_fetched + diff):
            with urllib.request.urlopen(self._hostname + f"/snapshot?index={idx}") as url:
                buf = url.read()
                sz_tot_buf += len(buf)
                    
            hex_str = buf.decode()
            buf = bytes.fromhex(hex_str)
            buf = zlib.decompress(buf)
            sz_decompr += len(buf)
            
            s = dill.loads(buf)
            self._snapshot_queue.put(s)
            self._snapshots_fetched += 1           

        if diff > 0:
            avg_sz_tot_buf = round(sz_tot_buf/diff/1000)
            avg_sz_decompr = round(sz_decompr/diff/1000)

            print(
                f"Downloaded {diff} snapshots. "
                f"Average download size: {avg_sz_tot_buf} kb, "
                f"Average decompressed size: {avg_sz_decompr} kb."
            )
        
