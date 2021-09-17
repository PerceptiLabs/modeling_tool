from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.automation.modelrecommender.decoders import DecoderBlueprint
import numpy as np


class MaskDecoderBlueprint(DecoderBlueprint):
    def build(self, builder: GraphSpecBuilder, feature_name: str, feature_spec: FeatureSpec, data_loader: DataLoader = None) -> str:
        """ Adds an decoder to the graph spec builder

        Arguments:
            builder: the entity used to construct the final graph
            feature_name: name of the current feature
            feature_spec: properties of the feature
        Returns:
            the ID of the decoders first layer
        """
        preprocessing = data_loader.get_preprocessing_pipeline(feature_name)
        target_shape = preprocessing.metadata['image_shape']
        num_feature_maps = target_shape[-1] # The number of feature maps should be equal to the number of channels
        n_neurons = np.prod(target_shape)

        id1 = builder.add_layer(
                'DeepLearningFC',
                settings={'n_neurons': n_neurons}
        )
        id2 = builder.add_layer(
                'ProcessReshape',
                settings={'shape': tuple(target_shape)}
        )

        id3 = builder.add_layer(
                'DeepLearningConv',
                settings={'conv_type': 'Transpose', 'stride':1, 'feature_maps': num_feature_maps}
        )

        id4 = builder.add_layer(
            'IoOutput',
            settings={'feature_name': feature_name, 'file_path': feature_spec.file_path, 'datatype': feature_spec.datatype}
        )
        builder.add_connection(id1, 'output', id2, 'input')
        builder.add_connection(id2, 'output', id3, 'input')
        builder.add_connection(id3, 'output', id4, 'input')
        return id1
