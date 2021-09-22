from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.automation.modelrecommender.encoders import EncoderBlueprint

# TODO: update docstrings w/ dataloader
class ImageEncoderBlueprint(EncoderBlueprint):
    def build(self, builder: GraphSpecBuilder, feature_name: str, feature_spec: FeatureSpec, data_loader: DataLoader = None) -> str:
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
            settings={'feature_name': feature_name, 'datatype': feature_spec.datatype}
        )
        id2 = builder.add_layer(
            'DeepLearningConv'
        )
        id3 = builder.add_layer(
            'DeepLearningFC',
            settings={'n_neurons': 128, 'activation': 'ReLU'}
        )
        builder.add_connection(id1, 'output', id2, 'input')
        builder.add_connection(id2, 'output', id3, 'input')
        return id3




