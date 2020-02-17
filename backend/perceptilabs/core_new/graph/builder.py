import copy
from typing import Dict, Tuple, Set
from abc import ABC, abstractmethod
import logging

from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import *
from perceptilabs.core_new.graph.base import Graph, JsonNetwork, Node
from perceptilabs.core_new.graph.utils import sanitize_layer_name

log = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self, replica_by_name=None):
        self._replica_by_name = replica_by_name    
    
    def build(self, layer_map: Dict[str, BaseLayer], edges_by_id: Set[Tuple[str, str]]):
        # TODO: remove this method?
        return self.build_from_layers_and_edges(layer_map, edges_by_id)
    
    def build_from_layers_and_edges(self, layer_map: Dict[str, BaseLayer], edges_by_id: Set[Tuple[str, str]]):        
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

    def build_from_snapshot(self, snapshot):
        if self._replica_by_name is None:
            raise RuntimeError("replica_by_name must be set in order to build from snapshot")

        replicas = {}
        for layer_id, layer_dict in snapshot['layers'].items():
            replica = self._build_replica(layer_dict)
            replicas[layer_id] = replica

        graph = self.build_from_layers_and_edges(replicas, snapshot['edges'])
        return graph
        
    def _build_replica(self, layer_dict):
        replica_class = self._replica_by_name.get(layer_dict['replica_class'])

        if replica_class is None:
            raise ValueError(f'No replica with name {layer_dict["replica_class"]} in. Check base_to_replica_map.')

        kwargs = {}
        for unique_key, value in layer_dict['properties'].items():
            _, key = unique_key.split('-')
            kwargs[key] = value        

        replica = replica_class(**kwargs)
        return replica
    
    def build_from_spec(self, graph_spec, session_config):
        graph_spec = graph_spec['Layers'] # TODO: remove!
        
        nodes = {}
        for layer_spec in graph_spec.values():
            layer_type = layer_spec['Type']

            #TODO: Remove this if-case when frontend is sending back correct file path on Windows
            if layer_type == "DataData":
                sources = layer_spec['Properties']['accessProperties']['Sources']
                new_sources = []
                for source in sources:
                    tmp = source
                    if tmp["path"]:
                        tmp["path"] = tmp["path"].replace("\\","/")
                    new_sources.append(tmp)
                layer_spec['Properties']['accessProperties']['Sources'] = new_sources

            layer_id = sanitize_layer_name(layer_spec['Name'])
            layer_instance = None#self._get_layer_instance(layer_id, layer_type, session_config['session_id'])
            node = Node(layer_id, layer_type, layer_instance, layer_spec)
            nodes[layer_id] = node

        print(nodes)
        edges = set()
        for layer_spec in graph_spec.values():
            from_id = sanitize_layer_name(layer_spec['Name'])
            fwd_cons = [sanitize_layer_name(layer_id)
                        for _, layer_id in layer_spec['forward_connections']]

            from_node = nodes[from_id]
            for to_id in fwd_cons:
                to_node = nodes[to_id]
                edges.add((from_node, to_node))

        graph = Graph(list(nodes.values()), list(edges))
        return graph

    
class SnapshotBuilder:
    def __init__(self, base_to_replica_map, replicated_properties_table, fn_can_serialize=None):
        self._base_to_replica_map = base_to_replica_map
        self._replicated_properties_table = replicated_properties_table
        self._fn_can_serialize = fn_can_serialize
        
        # TODO: inject compression, caching and that kind of stuff?
        
    def build(self, graph):
        layers_dict = {}
        for node in graph.nodes:
            layer_dict = self._build_layer_dict(node)
            layers_dict[node.layer_id] = layer_dict

        edges_list = []
        for edge in graph.edges:
            edge_tuple = (edge[0].layer_id, edge[1].layer_id)
            edges_list.append(edge_tuple)
        
        snapshot_dict = {
            'layers': layers_dict,
            'edges': edges_list
        }
        
        if (self._fn_can_serialize is not None) and (not self._fn_can_serialize(snapshot_dict)):
            raise RuntimeError("Serialization test failed")

        return snapshot_dict
            
    def _build_layer_dict(self, node):
        layer_dict = None
        for base_class, replica_class in self._base_to_replica_map.items():
            if isinstance(node.layer, base_class):
                layer_dict = self._build_layer_dict_internal(node, base_class, replica_class)
                break
            
        if layer_dict is None:
            raise ValueError(f'Layer class {type(node.layer)} not found in base_to_replica_map')
        return layer_dict

    def _build_layer_dict_internal(self, node, base_class, replica_class):
        replicated_props = self._replicated_properties_table.get(base_class)
        if replicated_props is None:
            raise ValueError(f'Base class {base_class} not found in replicated_properties_table')

        properties = {}
        for repl_prop in replicated_props:
            properties.update(self._get_replicated_property(node, repl_prop))

        result = {
            'replica_class': replica_class.__name__,
            'properties': properties
        }
        return result

    def _get_replicated_property(self, node, repl_prop):
        unique_key = f'{node.layer_id}-{repl_prop.name}'

        if not hasattr(node.layer, repl_prop.name):
            value = repl_prop.default(None) if callable(repl_prop.default) else repl_prop.default
            log.warning(f'Layer {node.layer_id} [{type(node.layer)}] missing attribute "{repl_prop.name}". Using default: {value}.')
            
        value = getattr(node.layer, repl_prop.name)
        if repl_prop.type is not None:
            valid_type = isinstance(value, repl_prop.type) or (isinstance(repl_prop, tuple) and type(value) in repl_prop)

            if not valid_type:
                default_value = repl_prop.default(None) if callable(repl_prop.default) else repl_prop.default                
                log.warning(
                    f'Layer {node.layer_id} [{type(node.layer)}] attribute "{repl_prop.name}" expected type(s) {repl_prop.type}, '
                    f'got {type(value)}. Using default: {default_value} [{type(default_value)}].'
                )
                value = default_value
        return {unique_key: value}
    

