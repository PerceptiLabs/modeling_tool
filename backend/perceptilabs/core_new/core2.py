import time
import uuid
import logging
import requests
import tempfile
import threading
import subprocess
from typing import Dict, List
from abc import ABC, abstractmethod

from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.deployment import DeploymentPipe
from perceptilabs.core_new.api.mapping import ByteMap


log = logging.getLogger(__name__)


class Core:
    def __init__(self, graph_builder: GraphBuilder, deployment_pipe: DeploymentPipe):
        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._graphs = []
        
        self._lock = threading.Lock()        
        self._is_running = threading.Event()
        self._is_running.clear()
        
    def run(self, graph_spec: JsonNetwork, session_id: str=None):
        session_id = session_id or uuid.uuid4().hex
        log.info(f"Starting core with session id {session_id}")

        self._is_running.set()        
        self._worker = threading.Thread(
            target=self._worker_func,
            args=(graph_spec, session_id),
            daemon=True
        )
        self._worker.start()

    def deploy(self, graph_spec, session_id):
        config = self._deployment_pipe.get_session_config(session_id)        
        graph = self._graph_builder.build_from_spec(graph_spec, config)        
        self._deployment_pipe.deploy(graph, config)
        self._graphs = []

    def step(self):
        self._fetch_graph(graph_spec, config)
            
    def _worker_func(self, graph_spec, session_id):
        log.debug(f"Entering worker thread for session id {session_id}")
        
        config = self._deployment_pipe.get_session_config(session_id)        
        graph = self._graph_builder.build_from_spec(graph_spec, config)        
        self._deployment_pipe.deploy(graph, config)
        self._graphs = []
        
        counter = 0
        time_start = time.time()
        while self._is_running.is_set():
            self._fetch_graph(graph_spec, config)

            graphs = self.graphs
            if len(graphs) > 0 and graphs[-1].nodes[-1].layer.status == 'finished':
                self._is_running.clear()

            if counter % 10 == 0:
                log.debug(f"Session {session_id} worker uptime: {time.time() - time_start}s")
                
            counter += 1
            time.sleep(0.5)



    def _fetch_graph(self, graph_spec, config):
        import urllib
        import zlib
        import dill

        try:
            with urllib.request.urlopen("http://localhost:5678/snapshot_count") as url:
                buf = url.read().decode()

            snapshot_count = int(buf)
            with self._lock:            
                graph_count = len(self._graphs)
                
            log.info(f"{snapshot_count} snapshots available at remote, {graph_count} graphs available locally.")
            if graph_count > 0:
                with self._lock:
                    epoch = self._graphs[-1].active_training_node.layer.epoch
                    log.info(f"Latest graph epoch: {epoch}")                

            diff = snapshot_count - graph_count
            n_fetch = min(diff, 50)
                    
            sz_tot_buffer = 0
            sz_tot_decompressed = 0
            for i in range(graph_count, graph_count + n_fetch):
                log.debug(f"Collecting graph {i-graph_count}/{n_fetch}")
                with urllib.request.urlopen(f"http://localhost:5678/snapshot?index={i}") as url:
                    buf = url.read()
                    sz_tot_buffer += len(buf)
                    
                hex_str = buf.decode()
                buf = bytes.fromhex(hex_str)
                buf = zlib.decompress(buf)
                sz_tot_decompressed += len(buf)
                
                snapshot = dill.loads(buf)
                graph = self._graph_builder.build_from_snapshot(snapshot)
                
                #if log.isEnabledFor(logging.DEBUG):
                #    from perceptilabs.utils import stringify
                #    text = stringify(snapshot, indent=4, sort=True)
                #    log.debug("snapshot_dict: \n" + text)
            
                with self._lock:
                    self._graphs.append(graph)

            if n_fetch > 0:
                log.info(
                    f"Collected {n_fetch}. "
                    f"Average download size: {sz_tot_buffer/n_fetch} bytes, "
                    f"average decompressed size {sz_tot_decompressed/n_fetch} bytes."
                )
        except Exception as e:
            log.exception("Error while fetching graph")
            print('error while fetching', repr(e))

    @property
    def graphs(self):
        with self._lock:
            return self._graphs

    def stop(self):
        pass

    def pause(self):
        requests.post("http://localhost:5678/command", json={'type': 'on_pause'})        
        
    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
