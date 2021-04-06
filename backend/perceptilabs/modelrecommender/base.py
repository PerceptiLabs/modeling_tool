from collections import namedtuple
from typing import Dict

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec

from perceptilabs.modelrecommender.encoders import (
    NumericalEncoderBlueprint,
    ImageEncoderBlueprint,
    BinaryEncoderBlueprint,
    CategoricalEncoderBlueprint
)
from perceptilabs.modelrecommender.decoders import (
    NumericalDecoderBlueprint,
    CategoricalDecoderBlueprint,
    ImageDecoderBlueprint
)


class ModelRecommender:
    def __init__(self, data_loader=None):
        self._data_loader = data_loader
    
    def get_graph(self, feature_specs: Dict[str, FeatureSpec]) -> GraphSpec:
        """ Takes a dictionary of feature specs and generates a graph spec for it 
        Arguments:
            feature_specs: Mapping from feature name to feature spec
        Returns:
            a GraphSpec
        """        
        builder = GraphSpecBuilder()        
        encoder_end_nodes = []
        decoder_start_nodes = []
        
        for feature_name, feature_spec in feature_specs.items():
            if feature_spec.iotype == 'input':
                end_node = self._add_encoder(builder, feature_name, feature_spec)
                encoder_end_nodes.append(end_node)
            elif feature_spec.iotype == 'output':
                start_node = self._add_decoder(builder, feature_name, feature_spec)
                decoder_start_nodes.append(start_node)
            else:
                raise ValueError(f"Feature {feature_name} must have iotype 'input' or 'output'")

        self._connect_encoders_and_decoders(builder, encoder_end_nodes, decoder_start_nodes)
        
        graph_spec = builder.build()
        return graph_spec

    def _connect_encoders_and_decoders(self, builder, encoder_end_nodes, decoder_start_nodes):
        """ Merges the encoders and feeds the merged output to the decoders. If single input/output, no merge layer is needed. """
        if len(encoder_end_nodes) == 1:
            combiner_id = encoder_end_nodes[0] 
        elif len(encoder_end_nodes) == 2:
            combiner_id = builder.add_layer('MathMerge')
            for i, layer_id in enumerate(encoder_end_nodes):
                builder.add_connection(layer_id, 'output', combiner_id, f'input{i}')
        else:
            # TODO(anton.k): to support more inputs than 2, MathMerge must support more than 2 inputs (fix in story 1546)
            raise NotImplementedError("A maximum of two input encoders are supported right now")                
        for layer_id in decoder_start_nodes:
            builder.add_connection(combiner_id, 'output', layer_id, 'input')
            
    def _add_encoder(self, builder, feature_name, feature_spec):
        """ Encoder for a feature """
        if feature_spec.datatype == 'numerical':
            return NumericalEncoderBlueprint().build(builder, feature_name, feature_spec, data_loader=self._data_loader)            
        elif feature_spec.datatype == 'image':
            return ImageEncoderBlueprint().build(builder, feature_name, feature_spec, data_loader=self._data_loader)            
        elif feature_spec.datatype == 'binary':
            return self._add_binary_encoder(builder, feature_name, feature_spec)
        elif feature_spec.datatype == 'categorical':
            return self._add_categorical_encoder(builder, feature_name, feature_spec, data_loader=self._data_loader)
        else:
            raise NotImplementedError(f"No encoder found for datatype '{feature_spec.datatype}'")

    def _add_decoder(self, builder, feature_name, feature_spec):
        """ Decoder for a feature """                
        if feature_spec.datatype == 'numerical':
            return NumericalDecoderBlueprint().build(builder, feature_name, feature_spec, data_loader=self._data_loader)
        elif feature_spec.datatype == 'categorical':
            return CategoricalDecoderBlueprint().build(builder, feature_name, feature_spec, data_loader=self._data_loader)       
        elif feature_spec.datatype == 'image':
            return ImageDecoderBlueprint().build(builder, feature_name, feature_spec, data_loader=self._data_loader)   
        else:
            raise NotImplementedError(f"No decoder found for datatype '{feature_spec.datatype}'")
        
    def _add_numerical_encoder(self, builder, feature_name, feature_spec):
        """ Adds a numerical encoder """
        return NumericalEncoderBlueprint().build(builder, feature_name, feature_spec)

    def _add_image_encoder(self, builder, feature_name, feature_spec):
        """ Adds a image encoder """
        return ImageEncoderBlueprint().build(builder, feature_name, feature_spec)
    
    def _add_binary_encoder(self, builder, feature_name, feature_spec):
        """ Adds a binary encoder """
        return BinaryEncoderBlueprint().build(builder, feature_name, feature_spec)

    def _add_categorical_encoder(self, builder, feature_name, feature_spec, data_loader):
        return CategoricalEncoderBlueprint().build(builder, feature_name, feature_spec, data_loader)
    
    def _add_numerical_decoder(self, builder, feature_name, feature_spec):
        """ Adds a numerical decoder """
        return NumericalDecoderBlueprint().build(builder, feature_name, feature_spec)

