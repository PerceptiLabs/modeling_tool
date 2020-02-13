import time
import uuid
import logging
import requests
import tempfile
import threading
import subprocess
from typing import Dict, List, Callable
from abc import ABC, abstractmethod

from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.deployment import DeploymentPipe
from perceptilabs.core_new.api.mapping import ByteMap
from perceptilabs.core_new.communication.status import *


log = logging.getLogger(__name__)


class Core:
    def __init__(self, graph_builder: GraphBuilder, deployment_pipe: DeploymentPipe):
        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._graphs = []
        
        self._lock = threading.Lock()        
        self._is_running = threading.Event()
        self._is_running.clear()
        
    def run(self, graph_spec: JsonNetwork, session_id: str=None, on_iterate: Callable=None):
        session_id = session_id or uuid.uuid4().hex
        log.info(f"Running core with session id {session_id}")

        config = self._deployment_pipe.get_session_config(session_id)        
        graph = self._graph_builder.build_from_spec(graph_spec, config)
        client = self._deployment_pipe.deploy(graph, config)


        log.info(f"Sending start command to deployed core with session id {session_id}")        
        client.start()
        while client.status in [STATUS_READY, STATUS_STARTED]:
            time.sleep(1.0)

        if client.status == STATUS_RUNNING:
            log.info(f"Deployed core with id {session_id} indicated status 'running'")         

        self._graphs = []        
        while client.status == STATUS_RUNNING or (client.status == STATUS_IDLE and len(self._graphs) < client.snapshot_count):
            snapshots = client.pop_snapshots()
            new_graphs = [self._graph_builder.build_from_snapshot(s) for s in snapshots]

            with self._lock:
                self._graphs.extend(new_graphs)

            if on_iterate is not None:
                on_iterate()                
            time.sleep(1)

        log.info(f"Sending stop command to deployed core with session id {session_id}")
        client.stop()
            
    @property
    def graphs(self):
        with self._lock:
            return self._graphs.copy()

    def stop(self):
        pass

    def pause(self):
        #requests.post("http://localhost:5678/command", json={'type': 'on_pause'})
        pass
        
    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
