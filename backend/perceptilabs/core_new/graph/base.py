import copy
import logging
import networkx as nx
from typing import Dict, List, Tuple


from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.core_new.layers.base import BaseLayer, DataLayer,  DataSupervised, DataRandom, DataReinforce, InnerLayer, TrainingLayer, TrainingSupervised, TrainingRandom, TrainingReinforce


logger = logging.getLogger(APPLICATION_LOGGER)


class Node:
    def __init__(self, layer_id, layer_type, layer_instance, layer_spec=None):
        self._layer_id = layer_id
        self._layer_instance = layer_instance
        self._layer_spec = layer_spec
        self._layer_type = layer_type

    @property
    def layer_id(self):
        return self._layer_id
        
    @property
    def layer_type(self):
        return self._layer_type

    @property
    def layer_spec(self):
        return copy.deepcopy(self._layer_spec)
        
    @property
    def is_training_node(self):
        return isinstance(self._layer_instance, TrainingLayer)    

    @property
    def is_data_node(self):
        return isinstance(self._layer_instance, DataLayer)

    @property
    def layer_instance(self):
        return self._layer_instance
    
    @property
    def layer(self):
        return self._layer_instance

    @property
    def custom_code(self):
        if self._layer_spec['Code'] is None or self._layer_spec['Code'] is '':
            return None

        if self._layer_spec['Code'].get('Output') is None:
            return None

        code = self._layer_spec['Code']['Output']
        return code
    

class Graph:
    def __init__(self, nodes: List[Node], edges: List[Tuple[Node, Node]]=None, connections=None):
        for n1, n2 in edges:
            assert n1 in nodes
            assert n2 in nodes        

        self._connections = connections or {}
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from(nodes)
        self._nx_graph.add_edges_from(edges or [])

        end_nodes = [n for n in self._nx_graph.nodes if len(list(self._nx_graph.successors(n))) == 0]
        if len(end_nodes) > 1:
            raise RuntimeError("Not supported. More than one _isolated_ subgraph detected!")
        
        # self._end_node = end_nodes[0]
        # bfs_tree = list(nx.bfs_tree(self._nx_graph, self._end_node, reverse=True))
        # self._ordered_nodes = tuple(reversed(bfs_tree))
        self._ordered_nodes = list(nx.algorithms.dag.topological_sort(self._nx_graph))

    def _find_subgraphs(self, nx_graph, start_node, searched):
        searched.add(start_node)
        nodes = list(nx.bfs_tree(nx_graph, start_node, reverse=True))

        subgraph = nx.subgraph(nx_graph, nodes)
        subgraphs = [subgraph]
        
        for node in nodes:
            if node.is_training_node and node not in searched:
                s = self._find_subgraphs(subgraph, node, searched)
                subgraphs.extend(s)
                
        return subgraphs
        
    @property
    def nodes(self):
        """ Nodes in order of execution. I.e., data layers first, training layers last """
        return list(self._ordered_nodes)

    @property
    def training_nodes(self):
        return [n for n in self._ordered_nodes if n.is_training_node]

    @property
    def data_nodes(self):
        return [n for n in self._ordered_nodes if n.is_data_node]

    @property
    def inner_nodes(self):
        return [n for n in self._ordered_nodes if not n.is_training_node and not n.is_data_node]

    @property
    def active_training_node(self):
        return self._end_node

    @property
    def trainable_subgraphs(self):
        """ Subgraphs in order of execution. I.e., complete graph last """
        nx_subgraphs = self._find_subgraphs(self._nx_graph, self._end_node, set())
        subgraphs = list(reversed([Graph(list(x.nodes), list(x.edges)) for x in nx_subgraphs]))
        return subgraphs
    
    def show(self):
        import matplotlib.pyplot as plt
        nx.draw(self._nx_graph)
        plt.show()

    def get_node_by_id(self, layer_id: str):
        target_nodes = [x for x in self.nodes if x.layer_id == layer_id]

        if len(target_nodes) == 0:
            raise RuntimeError(f"Node with id {layer_id} not in graph")
        if len(target_nodes) > 1:
            raise RuntimeError(f"Graph is corrupt. {len(target_nodes)} nodes have the id {layer_id}, expected one")

        return target_nodes[0]
    
    def get_input_nodes(self, node):
        input_nodes = self._nx_graph.predecessors(node)
        return input_nodes

    def get_input_connections(self, dst_node):
        result = []
        for src_node in self.get_input_nodes(dst_node):
            key = src_node.layer_id + ':' + dst_node.layer_id # layer id is the 'sanitized name'
            conns = self._connections.get(key, [])

            for src_var, dst_var in conns:
                result.append((src_node, src_var, dst_var))
                
        return result    

    def get_direct_data_nodes(self, layer_id: str):
        """ Select data layers that are immediately connected to the layer """
        target_node = self.get_node_by_id(layer_id)
        
        result = []
        if target_node.is_data_node:
            result.append(target_node)        

        for data_node in self.data_nodes:
            # TODO: can we use ancesotrs instead?
            simple_paths = list(nx.all_simple_paths(self._nx_graph, data_node, target_node))

            if len(simple_paths) > 0:
                immediate = True # Assume all connections are immediate (pass through only one data node) and then verify that.
                for path in simple_paths:
                    data_nodes_in_path = [n for n in path if n.is_data_node]

                    if not (
                            data_nodes_in_path == [data_node] or
                            data_nodes_in_path == [data_node, target_node]
                    ):
                        immediate = False
                        break

                if immediate:
                    result.append(data_node)
                
        return result

    @property
    def active_training_node(self):
        return self.nodes[-1] # TODO : adapt this for split graph

    def run(self):
        yield from self.active_training_node.layer.run(self)

    def on_stop(self):
        self.active_training_node.layer.on_stop()        
        
    def on_export(self, path, mode):
        self.active_training_node.layer.on_export(path, mode)        

    def on_headless_activate(self):
        self.active_training_node.layer.on_headless_activate()        

    def on_headless_deactivate(self):
        self.active_training_node.layer.on_headless_deactivate()        
        
    @property
    def edges(self):
        return self._nx_graph.edges    
    
    def get_nodes_inbetween(self, source, target):
        paths_between_generator = nx.all_simple_paths(self._nx_graph, source, target)
        nodes_between_list = [node for path in paths_between_generator for node in path]
        return nodes_between_list[1:]

    def clone(self): 
        from perceptilabs.core_new.graph.builder import GraphBuilder
        layers = {}
        
        for node in self.nodes:
            layer = node.layer.__class__()        
            try:
                # TODO: make this work properly in the InnerLayer constructor
                layer._scope = layer._scope + '_copy'
            except:
                pass
            else:                                                                                                                                                                                       
                logger.warning(f"Overwrote protected field '_scope' in layer {node.layer_id}")
            layers[node.layer_id] = layer
            
        builder = GraphBuilder()
        edges_by_id = [(a.layer_id, b.layer_id) for a, b in self._nx_graph.edges]
        new_graph = builder.build_from_layers_and_edges(layers, edges_by_id, connections=self._connections)
        return new_graph       
