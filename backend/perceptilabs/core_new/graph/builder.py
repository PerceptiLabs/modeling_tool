import copy
from typing import Dict, Tuple, Set
from abc import ABC, abstractmethod
import logging

from perceptilabs.core_new.layers.communication import BaseClient, BaseServer
from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import *
from perceptilabs.core_new.graph.utils import breadth_first_sort
from perceptilabs.core_new.graph.base import Graph, JsonNetwork, Node
from perceptilabs.core_new.layers.communication import BaseClient


log = logging.getLogger(__name__)


class GraphBuilder:
    def build(self, layer_map: Dict[str, BaseLayer], edges_by_id: Set[Tuple[str, str]]):
        nodes = {}
        for layer_id, layer_instance in layer_map.items():
            node = Node(layer_id, None, layer_instance, None)
            nodes[layer_id] = node

        edges = []
        for edge_by_id in edges_by_id:
            from_node = nodes[edge_by_id[0]]
            to_node = nodes[edge_by_id[1]]
            edges.append((from_node, to_node))
            
        graph = Graph(list(nodes.values()), edges)
        return graph

        

class ReplicatedGraphBuilder:
    def __init__(self, client):
        self._client = client
        
    def build(self, graph_spec, session_config, state_map=None):
        state_map = state_map or {}
        graph_spec = graph_spec['Layers'] # TODO: remove!
        
        nodes = {}
        for layer_id, layer_spec in graph_spec.items():
            layer_type = layer_spec['Type']
            layer_instance = self._get_layer_instance(layer_id, layer_type, session_config['session_id'], state_map)
            node = Node(layer_id, layer_type, layer_instance, layer_spec)
            nodes[layer_id] = node

        edges = set()
        for from_id, layer_spec in graph_spec.items():
            fwd_cons = layer_spec['forward_connections']

            from_node = nodes[from_id]
            for to_id in fwd_cons:
                to_node = nodes[to_id]
                edges.add((from_node, to_node))

        graph = Graph(list(nodes.values()), list(edges))
        return graph
            
    def _get_layer_instance(self, layer_id, layer_type, session_id, state_map):
        layer_def = DEFINITION_TABLE.get(layer_type)

        if layer_def is not None:
            if issubclass(layer_def.base_class, Tf1xClassificationLayer):

                result = Tf1xClassificationLayerReplica(
                    sample=state_map.get(layer_id + '-sample'),
                    size_training=state_map.get(layer_id + '-size_training'),
                    size_validation=state_map.get(layer_id + '-size_validation'),
                    size_testing=state_map.get(layer_id + '-size_testing'),
                    variables=state_map.get(layer_id + '-variables'),
                    accuracy_training=state_map.get(layer_id + '-accuracy_training'),
                    accuracy_testing=state_map.get(layer_id + '-accuracy_testing'),
                    accuracy_validation=state_map.get(layer_id + '-accuracy_validation'),
                    loss_training=state_map.get(layer_id + '-loss_training'),
                    loss_testing=state_map.get(layer_id + '-loss_testing'),
                    loss_validation=state_map.get(layer_id + '-loss_validation'),
                    status=state_map.get(layer_id + '-status'),                    
                )
            elif issubclass(layer_def.base_class, DataLayer):
                result = DataLayerReplica(
                    sample=state_map.get(layer_id + '-sample'),
                    size_training=state_map.get(layer_id + '-size_training'),
                    size_validation=state_map.get(layer_id + '-size_validation'),
                    size_testing=state_map.get(layer_id + '-size_testing'),
                    variables=state_map.get(layer_id + '-variables'),
                )                
            elif issubclass(layer_def.base_class, Tf1xLayer):                
                result = Tf1xLayerReplica(
                    variables=state_map.get(layer_id + '-variables'),
                    trainable_variables=state_map.get(layer_id + '-trainable_variables'),
                )
        else:
            raise ValueError(f"Failed finding a replica class for layer type '{layer_type}'")
        return result

"""
class BaseStrategy(ABC):
    def _get_ordered_spec(self, graph_spec):
        # Perform a breadth first search by using the last training layer as the root node.
        bwd_cons = {k: v['backward_connections'] for k, v in graph_spec['Layers'].items()}
        end_nodes = [k for k, v in graph_spec['Layers'].items() if len(v['forward_connections']) == 0]
        
        assert len(end_nodes) == 1
        order = reversed(breadth_first_sort(bwd_cons, end_nodes[0])) # We visited the training layer first, but we want to execute that last.

        new_spec = {"Layers": {id_: copy.deepcopy(graph_spec['Layers'][id_]) for id_ in order}}
        return new_spec                    
    
    def build(self, graph_spec: JsonNetwork, session_config: Dict[str, str]):
        ordered_spec = self._get_ordered_spec(graph_spec)

        nodes = {}
        for layer_id, layer_spec in ordered_spec['Layers'].items():
            layer = self._get_layer_instance(layer_id, layer_spec, session_config)

            if layer == 'deployedgraphstratnotworking':
                # hack hack
                layer = graph_spec['Layers'][layer_id]
            
            nodes[layer_id] = Node(layer_id, layer, layer_spec)

        graph = Graph(nodes)
        return graph

    @abstractmethod
    def _get_layer_instance(self, layer_id: str, layer_spec: Dict, session_config: Dict):
        raise NotImplementedError
    
    
class DeployedGraphStrategy(BaseStrategy):
    def __init__(self, server: BaseServer):
        self._server = server

    def _get_layer_instance(self, layer_id: str, layer_spec: Dict, session_config: Dict):
        return 'deployedgraphstratnotworking'


class ReplicatedGraphStrategy(BaseStrategy):
    def __init__(self, client: BaseClient):
        self._client = client
        
    def _get_layer_instance(self, layer_id: str, layer_spec: Dict, session_config: Dict):
        layer_type = layer_spec['Type']
        session_id = session_config['session_id']        
        layer_def = DEFINITION_TABLE.get(layer_type)

        if layer_def is not None:
            if issubclass(layer_def.base_class, TrainingLayer):
                result = TrainingLayerReplica(session_id, layer_id, self._client)
            elif issubclass(layer_def.base_class, DataLayer):
                result = DataLayerReplica(session_id, layer_id, self._client)
            elif issubclass(layer_def.base_class, Tf1xLayer):                
                result = Tf1xLayerReplica(session_id, layer_id, self._client)        
        else:
            raise ValueError(f"Failed finding a replica class for layer type '{layer_type}'")

        log.debug(f"Layer of type '{layer_type}' yielded a layer of type {type(result)}")
        return result
    
class GraphBuilder:
    def __init__(self, strategy='default', client=None, server=None):
        if strategy in ['default', 'deployed']:
            self._strategy = DeployedGraphStrategy(server)
        elif strategy == 'replicated':
            assert client is not None
            self._strategy = ReplicatedGraphStrategy(client)
        else:
            raise ValueError(
                f"strategy must be 'default', 'deployed' or 'replicated', not '{strategy}'"
            )

    def build(self, graph_spec: JsonNetwork, session_config: Dict[str, str]):                
        return self._strategy.build(graph_spec, session_config)
"""
