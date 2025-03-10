from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.automation.modelrecommender.decoders import DecoderBlueprint

# TODO: update docstrings w/ dataloader
class CategoricalDecoderBlueprint(DecoderBlueprint):
    def build(
        self,
        builder: GraphSpecBuilder,
        feature_name: str,
        feature_spec: FeatureSpec,
        data_loader: DataLoader = None,
    ) -> str:
        """Adds an decoder to the graph spec builder

        Arguments:
            builder: the entity used to construct the final graph
            feature_name: name of the current feature
            feature_spec: properties of the feature
        Returns:
            the ID of the decoders first layer
        """

        preprocessing = data_loader.get_preprocessing_pipeline(feature_name)
        n_categories = preprocessing.n_categories

        id1 = builder.add_layer(
            "DeepLearningFC",
            settings={"n_neurons": n_categories, "activation": "Softmax"},
        )
        id2 = builder.add_layer(
            "IoOutput",
            settings={
                "name": feature_name,
                "feature_name": feature_name,
                "datatype": feature_spec.datatype,
            },
        )
        builder.add_connection(id1, "output", id2, "input")
        return id1
