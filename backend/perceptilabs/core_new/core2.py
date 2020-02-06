import time
import uuid
import logging
import tempfile
import threading
import subprocess
from typing import Dict, List
from abc import ABC, abstractmethod

from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import ReplicatedGraphBuilder, GraphBuilder
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

            #if self.graph.nodes[-1].layer.status == 'done':
            #    self._is_running.clear()

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


            for i in range(graph_count, min(snapshot_count, graph_count + 50)):
                log.debug(f"Collecting graph {i}/{snapshot_count}")
                with urllib.request.urlopen(f"http://localhost:5678/snapshot?index={i}") as url:
                    buf = url.read().decode()
            
                buf = bytes.fromhex(buf)
                buf = zlib.decompress(buf)
                snapshot = dill.loads(buf)
                graph = self._graph_builder.build_from_snapshot(snapshot)
                
                #if log.isEnabledFor(logging.DEBUG):
                #    from perceptilabs.utils import stringify
                #    text = stringify(snapshot, indent=4, sort=True)
                #    log.debug("snapshot_dict: \n" + text)
            
                with self._lock:
                    self._graphs.append(graph)
                    
        except Exception as e:
            log.exception("Error while fetching graph")

    @property
    def graphs(self):
        with self._lock:
            return self._graphs

    def stop(self):
        pass

        
    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
