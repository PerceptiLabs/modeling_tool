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

        config = self._deployment_pipe.get_session_config(session_id)        
        graph = self._graph_builder.build_from_spec(graph_spec, config)
        client = self._deployment_pipe.deploy(graph, config)
        self._graphs = []



        time.sleep(1)
        print("START CORE!!!")
        client.start()


        print("START CORE CALLEEEED!!!")
        
        while client.status in ['ready', 'running'] or len(self._graphs) < client.snapshot_count:
            print('CLIENT STATUS', client.status, 'SNAPSHOT COUNT', client.snapshot_count, len(self._graphs))
            snapshots = client.pop_snapshots()
            new_graphs = [self._graph_builder.build_from_snapshot(s) for s in snapshots]
                
            with self._lock:
                self._graphs.extend(new_graphs)

            print("popped snapshots:", len(snapshots))
            print("total graphs:", len(self._graphs), client.snapshot_count)
            time.sleep(1)

        print("EXITED LOOP, STOP CORE! collected" , len(self._graphs), client.snapshot_count)
        
        client.stop()

            
    @property
    def graphs(self):
        with self._lock:
            return self._graphs

    def stop(self):
        pass

    def pause(self):
        #requests.post("http://localhost:5678/command", json={'type': 'on_pause'})
        pass
        
    @property
    def is_running(self):
        return self._is_running.is_set() 

        
            

    
        

    
