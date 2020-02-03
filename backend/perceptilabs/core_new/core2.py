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
        self._graph = None
        
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

    def _worker_func(self, graph_spec, session_id):
        log.debug(f"Entering worker thread for session id {session_id}")
        
        config = self._deployment_pipe.get_session_config(session_id)        
        self._graph = self._graph_builder.build(graph_spec, config)        
        self._deployment_pipe.deploy(self._graph, config)

        counter = 0
        time_start = time.time()
        while self._is_running.is_set():
            self._fetch_graph(graph_spec, config)

            if self.graph.nodes[-1].layer.status == 'done':
                self._is_running.clear()

            if counter % 10 == 0:
                log.debug(f"Session {session_id} worker uptime: {time.time() - time_start}s")
                
            counter += 1
            time.sleep(1)

    def _fetch_graph(self, graph_spec, config):
        import urllib
        import zlib
        import dill

        try:
            with urllib.request.urlopen("http://localhost:5678/state") as url:
                buf = url.read().decode()
            
            buf = bytes.fromhex(buf)
            buf = zlib.decompress(buf)
            state_map = dill.loads(buf)

            with self._lock:
                self._graph = self._graph_builder.build(graph_spec, config, state_map)
        except Exception as e:
            log.exception("Error while fetching graph")

    @property
    def graph(self):
        with self._lock:
            return self._graph

    def stop(self):
        pass

        
    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
