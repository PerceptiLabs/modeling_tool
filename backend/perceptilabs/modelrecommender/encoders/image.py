from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec
from perceptilabs.modelrecommender.encoders import EncoderBlueprint


class ImageEncoderBlueprint(EncoderBlueprint):
    def build(self, builder: GraphSpecBuilder, feature_name: str, feature_spec: FeatureSpec) -> str:
        """ Adds an encoder to the graph spec builder
        
        Arguments:
            builder: the entity used to construct the final graph
            feature_name: name of the current feature
            feature_spec: properties of the feature
        Returns:
            the ID of the encoders final layer
        """
        id1 = builder.add_layer(
            'IoInput',
            settings={'feature_name': feature_name, 'file_path': feature_spec.file_path, 'datatype': feature_spec.datatype}                
        )
        id2 = builder.add_layer(
            'DeepLearningConv'
        )
        builder.add_connection(id1, 'output', id2, 'input')
        return id2
        
    
    
    
