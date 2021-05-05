from collections import defaultdict
from typing import Dict, Any

from perceptilabs.layers.definitions import DEFINITION_TABLE_TF2X as DEFINITION_TABLE
from perceptilabs.layers.specbase import LayerConnection, sanitize_name
from perceptilabs.graph.spec import GraphSpec


TYPE_TO_NAME_TABLE = {
    'DeepLearningConv': 'Convolution',
    'DeepLearningFC': 'Dense',
    'DeepLearningRecurrent': 'Recurrent',
    'ProcessReshape': 'Reshape',
    'ProcessRescale': 'Rescale',
    'ProcessOneHot': 'OneHot',
    'MathSwitch': 'Switch',
    'ProcessGrayscale': 'Grayscale',
    'MathMerge': 'Merge',
    'PreTrainedVGG16': 'VGG16',
    'PreTrainedMobileNetV2': 'MobileNetV2',
    'PreTrainedResNet50': 'ResNet50',
    'PreTrainedInceptionV3': 'InceptionV3',
    'IoInput': 'Input',
    'IoOutput': 'Output',
}



class GraphSpecBuilder:
    def __init__(self):
        self._name_counter = {}
        self._id_counter = 0
        self._layers = {}
        self._connections = defaultdict(list)
        self._definitions = DEFINITION_TABLE        
    
    def add_layer(self, type_: str, settings: Dict[str, Any] = None):
        """ Add a layer to the graph

        Arguments:
            type_: the layer type to add
            settings: optional dict of keyword arguments to instantiate the layer with

        Returns:
            the ID of the new layer
        """
        settings = settings or {}
        settings['type_'] = type_
        if type_ not in self._name_counter:
            self._name_counter[type_] = 1

        if 'name' not in settings:
            settings['name'] = self._next_name(type_)
        if 'id_' not in settings:
            settings['id_'] = self._next_id()

        id_ = settings['id_']
        self._layers[id_] = settings
        self._name_counter[type_] += 1
        self._id_counter += 1

        return id_

    def add_connection(self, source_id: str, source_var: str, dest_id: str, dest_var: str):
        """ Adds a connection between two layers
        
        Arguments:
            source_id: the source layer
            source_var: the source variable
            dest_id: the destination layer
            dest_var: the destination variable
        """
        connection = LayerConnection(
            src_id=source_id, src_var=source_var,
            dst_id=dest_id, dst_var=dest_var
        )
        self.add_connection_object(connection)

    def add_connection_object(self, connection):
        """ Adds a connection between two layers
        
        Arguments:
            connection: LayerConnection object
        """
        self._connections[connection.src_id].append(connection)
        self._connections[connection.dst_id].append(connection)

    def _build_layer(self, layer_id):
        """ Build a layer 
        
        Arguments:
            layer_id: str
        """
        settings = self._layers[layer_id]
        settings['forward_connections'] = tuple([
            connection
            for connection in self._connections[layer_id]
            if connection.src_id == layer_id           
        ])
        settings['backward_connections'] = tuple([
            connection
            for connection in self._connections[layer_id]
            if connection.dst_id == layer_id           
        ])
        
        type_ = settings['type_']
        layer_spec = self._definitions[type_].spec_class(**settings)
        return layer_spec

    def build(self) -> GraphSpec:
        """ Builds the specified graph. 

        Returns:
            A graph spec
        """ 
        layer_specs = [
            self._build_layer(layer_id)
            for layer_id in self._layers
        ]
        graph_spec = GraphSpec(layer_specs)
        return graph_spec
        
    def _next_name(self, type_):
        """ Generate a layer name """
        try:
            clean_name = TYPE_TO_NAME_TABLE[type_]
        except:
            clean_name = type_
        return f"{clean_name}_{self._name_counter[type_]}"

    def _next_id(self):
        """ Generate a layer ID """        
        return str(self._id_counter)
        
        
            
        
