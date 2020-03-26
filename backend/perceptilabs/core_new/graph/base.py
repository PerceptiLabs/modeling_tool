import copy
import networkx as nx
from typing import Dict, List, Tuple


from perceptilabs.script.base import CodeGenerator
from perceptilabs.core_new.layers.base import BaseLayer, DataLayer, InnerLayer, TrainingLayer

class JsonNetwork(Dict):
    pass


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
    

class Graph:
    def __init__(self, nodes: List[Node], edges: List[Tuple[Node, Node]]=None):
        for n1, n2 in edges:
            assert n1 in nodes
            assert n2 in nodes        
        
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from(nodes)
        self._nx_graph.add_edges_from(edges or [])

        end_nodes = [n for n in self._nx_graph.nodes if len(list(self._nx_graph.successors(n))) == 0]
        if len(end_nodes) > 1:
            raise RuntimeError("Not supported. More than one _isolated_ subgraph detected!")

        self._end_node = end_nodes[0]

        bfs_tree = list(nx.bfs_tree(self._nx_graph, self._end_node, reverse=True))
        self._ordered_nodes = tuple(reversed(bfs_tree))

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
        print(layer_id, target_nodes)
        
        assert len(target_nodes) == 1
        return target_nodes[0]
    
    def get_input_nodes(self, node):
        input_nodes = self._nx_graph.predecessors(node)
        return input_nodes

    def get_direct_data_nodes(self, layer_id: str):
        """ Select data layers that are immediately connected to the layer """

        target_node = self.get_node_by_id(layer_id)
        print("target node", target_node.layer_instance)
        
        result = []

        for data_node in self.data_nodes:
            # TODO: can we use ancesotrs instead?
            simple_paths = list(nx.all_simple_paths(self._nx_graph, data_node, target_node))

            if len(simple_paths) > 0:
                immediate = True # Assume all connections are immediate and then verify that.
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

    @property
    def edges(self):
        return self._nx_graph.edges    
    
#    def clone(self):
#        layers = {n.layer_id: node.layer.__class__() for n in self.nodes}
#        new_graph = self._builder.build(layers, self._nx_graph.edges)
#        return new_graph

    
        
"""

class Node:
    def __init__(self, layer_id: str, layer: BaseLayer, layer_spec: Dict):
        self._layer_id = layer_id
        self._layer = layer
        self._spec = layer_spec

    @property
    def layer_id(self):
        return self._layer_id
    
    @property
    def layer(self):
        return self._layer
        
    @property
    def input_ids(self):
        ids = self._spec['backward_connections'].copy()
        return ids

    @property
    def layer_spec(self):
        return copy.deepcopy(self._spec)
""" 
'''        

class Graph:
    def __init__(self, nodes: Dict[str, Node]):
        self._nodes = nodes
        
    @classmethod
    def from_json(self):
        pass

    def get_data_dependencies(self, layer: BaseLayer):
        data_layers = []        
        node = self._nodes[layer]
        for input_id in node.inputs_ids:
            input_layer = self._nodes[input_id]            
            if isinstance(input_layer, DataLayer):
                data_layers.append(input_layer)
            data_layers.extend(self.get_data_dependencies(input_layer))
        return data_layers

    @property
    def inner_nodes(self):
        inner = {layer: node for layer, node in self._nodes.items() if isinstance(layer, InnerLayer)}
        return inner

    @property
    def nodes(self):
        return self._nodes.values()

    @property
    def active_training_layer(self):
        active_training_layers = [tl for tl in self.training_layers if tl.is_active]
        if len(active_training_layers) > 0:
            return active_training_layers[-1]
        else:
            return None        
    
    @property
    def active_subgraph(self):
        active_subgraphs = [s for s in self.subgraphs if s.training_layer.is_active]
        if len(active_subgraphs) > 0:
            return active_subgraphs[-1]
        else:
            return None        

    @property
    def training_layer(self):
        self.training_layers[-1]


    @property
    def training_layers(self):
        layers = [n.layer for n in self._nodes.values()]        
        print(self, 'layers',layers)
        print(self, 'types',[type(x) for x in layers])        
        layers = [n.layer for n in self._nodes.values() if isinstance(n.layer, TrainingLayer)]
        return layers
    
    @property
    def subgraphs(self):
        # TODO: implement properly. For now, subgraphs are not supported.
        return [self]

    
'''
