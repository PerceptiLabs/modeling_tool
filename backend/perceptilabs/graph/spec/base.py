import logging
import networkx as nx
from collections import namedtuple
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.graph.spec.layers import LayerSpec, get_layer_builder

logger = logging.getLogger(APPLICATION_LOGGER)
    
class GraphSpec(ABC):
    def __init__(self, nodes: List[LayerSpec], edges: List[Tuple[LayerSpec]]):
        self._nx_graph = nx.DiGraph()

        self._nx_graph.add_nodes_from([n.id for n in nodes])
        self._nx_graph.add_edges_from([(n1.id, n2.id) for n1, n2 in edges])
        self.nodes_by_id = {n.id: n for n in nodes}

    def to_dict(self):
        dict_ = {}
        for id_, node in self.nodes_by_id.items():
            builder = get_layer_builder(node.type)
            dict_[id_] = builder.to_dict(node)
        return dict_

    @classmethod
    def from_dict(cls, dict_):
        if 'Layers' in dict_:
            dict_ = dict_['Layers']
        
        id_to_node = {}
        edges_by_id = []
        
        for id_, json_layer in dict_.items():
            type_ = json_layer['Type']
            layer_spec_dict = dict_[id_]
            try:
                layer_spec = get_layer_builder(type_).from_dict(id_, layer_spec_dict).build()
            except:
                from perceptilabs.utils import stringify
                logger.error("Failed building layer from dict: {}".format(stringify(layer_spec_dict)))
                raise
            id_to_node[id_] = layer_spec

        edges_by_id = []        
        for from_id, json_layer in dict_.items():
            for to_id, _ in json_layer['forward_connections']:
                edges_by_id.append((from_id, to_id))

        edges = [(id_to_node[from_id], id_to_node[to_id]) for from_id, to_id in set(edges_by_id)]
        nodes = list(id_to_node.values())
        return cls(nodes, edges)

    @property
    def nodes(self) -> List[LayerSpec]:
        return list(self._nx_graph.nodes)

    @property
    def edges(self) -> List[LayerSpec]:
        return list(self._nx_graph.edges)
    
    def __getitem__(self, key):
        return self.nodes_by_id[key]

    def get_successors(self, layer_spec: LayerSpec):
        return [self.__getitem__(id) for id in self._nx_graph.successors(layer_spec.id)]
                
    def get_predecessors(self, layer_spec: LayerSpec):
        return [self.__getitem__(id) for id in self._nx_graph.predecessors(layer_spec.id)]        
                
    @property
    def node_ids(self):
        return list(self.nodes_by_id.keys())

    @property
    def edges_by_id(self):
        return [(x[0].id, x[1].id) for x in self._nx_graph.edges()]

    def get_subgraph(self, layer_ids):
        graph = self._nx_graph.subgraph(layer_ids)

        nodes = [graph.nodes_by_id[id] for id in graph.nodes]
        edges = [(graph.nodes_by_id[id1], graph.nodes_by_id[id2]) for id1, id2 in graph.edges]
        return GraphSpec(list(graph.nodes), list(graph.edges))
        

        

if __name__ == "__main__":

    n_classes = 10    
    inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"

    json_network = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [["3", "reshape"]],
                "Code": None,
                "checkpoint": []
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Batch_size": 8,
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [["5", "one_hot"]],
                "Code": None,
                "checkpoint": []
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [["1", "data_inputs"]],
                "forward_connections": [["4", "fc"]],
                "Code": None,
                "checkpoint": []
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1"
                },
                "backward_connections": [["3", "reshape"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [["2", "data_labels"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 200,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Batch_size": 10,                    
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Learning_rate": "0.05",
                    "Distributed": False
                },
                "backward_connections": [["4", "fc"], ["5", "one_hot"]],
                "forward_connections": [],
                "Code": None,
                "checkpoint": []
            }
        }
    }


    import time


    t0 = time.perf_counter()
    graph_spec = GraphSpec.from_dict(json_network)
    t1 = time.perf_counter()
    print('from_dict:', t1-t0)

    #ll=json_network['Layers']['4']['Properties']
    n = 10000
    t0 = time.perf_counter()
    for i in range(n):
        ll=json_network['Layers']['4']['Properties']['Activation_function']
    t1 = time.perf_counter()
    dt1 = (t1-t0)/n


    #ll = graph_spec.get_layer_by_id('4')
    t0 = time.perf_counter()
    for i in range(n):
        ll = graph_spec.nodes_by_id['4'].activation
        #ll.activation        
    t1 = time.perf_counter()
    dt2 = (t1-t0)/n


    print('old/new: ', dt1/dt2)

    
    
    import pdb; pdb.set_trace()

