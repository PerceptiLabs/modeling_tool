import time
import uuid
import tempfile
import subprocess
from queue import Queue
from typing import Dict, List
from abc import ABC, abstractmethod

from perceptilabs.core_new.graph import Graph, JsonNetwork
from perceptilabs.core_new.graph.builder import ReplicatedGraphBuilder, GraphBuilder
from perceptilabs.core_new.layers import TrainingLayer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.deployment import DeploymentPipe
from perceptilabs.core_new.api.mapping import ByteMap

            
class Core:
    def __init__(self, graph_builder: GraphBuilder, deployment_pipe: DeploymentPipe,
                 command_queue: Queue, result_queue: Queue):

        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._command_queue = command_queue
        self._result_queue = result_queue
        
    def run(self, graph_spec: JsonNetwork, session_id: str=None):
        session_id = session_id or uuid.uuid4().hex        
        config = self._deployment_pipe.get_session_config(session_id)        
        graph = self._graph_builder.build(graph_spec, config)        
        self._deployment_pipe.deploy(graph, session_id)

        self._graph_spec = graph_spec
        self._config = config
        
        #self._state_map = ByteMap(
        #    session_id,
        #    'tcp://localhost:5556',
        #    'tcp://localhost:5557',
        #    'tcp://localhost:5558'
        #)


        self._graph = self._graph_builder.build(self._graph_spec, self._config, {})        
        #self._state_map.start()            
        '''
        counter = 0
        while self._deployment_pipe.is_active or counter == 0:
            time.sleep(0.1)
            
            #self._handle_frontend_commands(graph)            
            #self._handle_userland_state(graph)
            #self._handle_file_transfers()

            l = self.graph.nodes[-1].layer
            print(l)

            print(l.accuracy_training)
            
            #core.graph.training_nodes[0].layer.sample
            #import pdb;pdb.set_trace()
            #s = l.sample
            #s = None
            #if s is not None:
            #    print(counter, s.shape)

            counter += 1
        '''

    def stop(self):
        # TODO: deploy stop
        self._state_map.stop()
        
    def get_graph(self):
        #print("GRAPH")
        import urllib
        import zlib
        import dill

        try:
            with urllib.request.urlopen("http://localhost:5678/state/") as url:
                buf = url.read().decode()
            
            buf = bytes.fromhex(buf)
            buf = zlib.decompress(buf)
            state_map = dill.loads(buf) 
            self._graph = self._graph_builder.build(self._graph_spec, self._config, state_map)
        except Exception as e:
            print(repr(e))
        finally:
            return self._graph

    @property
    def is_running(self):
        return self._deployment_pipe.is_active # for now... maybe need direct pipe to script?


    '''
    def _handle_userland_state(self, graph: Graph):
        node = graph.active_training_node    
        policy = DEFINITION_TABLE.get(node.layer_type).data_policy()
        
        if policy is not None:
            results = policy.get_results(graph)
        else:
            # TODO: No policy specified for this training layer and status. warning message? 
            pass
        
    def _handle_frontend_commands(self, graph: Graph):
        while not self._command_queue.empty():
            command, args, kwargs = self._command_queue.get(), {}, {}
            for layer in graph.training_layers:
                self._handle_frontend_command(layer, command, args, kwargs)

    def _handle_frontend_command(layer: TrainingLayer, command: str, args: Dict, kwargs: Dict):
        event_map = {
            'pause': layer.on_pause
        }
        if command in event_map:
            handler = event_map[command]
            handler(*args, **kwargs)
        else:
            # TODO: warning?
            pass
    '''

            
        

        


    
