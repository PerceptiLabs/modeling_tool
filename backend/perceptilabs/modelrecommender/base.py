from collections import namedtuple
from typing import Dict

from perceptilabs.graph.spec import GraphSpec
from perceptilabs.graph.builder import GraphSpecBuilder

FeatureSpec = namedtuple('FeatureSpec', ['datatype', 'iotype', 'csv_path'])


class ModelRecommender:
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
                end_node = self._add_encoder(
                    feature_name, feature_spec.datatype, feature_spec.csv_path, builder
                )
                encoder_end_nodes.append(end_node)
            elif feature_spec.iotype == 'output':
                start_node = self._add_decoder(
                    feature_name, feature_spec.datatype, feature_spec.csv_path, builder
                )
                decoder_start_nodes.append(start_node)
            else:
                raise ValueError(f"Feature {feature_name} must have iotype 'input' or 'output'")

        self._connect_encoders_and_decoders(encoder_end_nodes, decoder_start_nodes, builder)
        
        graph_spec = builder.build()
        return graph_spec

    def _connect_encoders_and_decoders(self, encoder_end_nodes, decoder_start_nodes, builder):
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
            
    def _add_encoder(self, feature_name, datatype, csv_path, builder):
        """ Encoder for a feature """
        if datatype == 'numerical':
            id_ = builder.add_layer(
                'IoInput',
                settings={'feature_name': feature_name, 'file_path': csv_path}
            ) 
            return id_
        else:
            raise NotImplementedError(f"No encoder found for datatype '{datatype}'")

    def _add_decoder(self, feature_name, datatype, csv_path, builder):
        """ Decoder for a feature """        
        if datatype == 'numerical':
            id1 = builder.add_layer(
                'DeepLearningFC',
                settings={'n_neurons': 1, 'activation': 'None'}
            )
            id2 = builder.add_layer(
                'IoOutput',
                settings={'feature_name': feature_name, 'file_path': csv_path}
            ) 
            builder.add_connection(id1, 'output', id2, 'input') 
            return id1           
        else:
            raise NotImplementedError(f"No decoder found for datatype '{datatype}'")    
        
