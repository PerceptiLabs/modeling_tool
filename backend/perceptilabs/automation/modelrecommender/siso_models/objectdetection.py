from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.automation.modelrecommender.siso_models import SISOModelBlueprint
import numpy as np


class ObjectDetectionModel(SISOModelBlueprint):
    def build(
        self,
        builder: GraphSpecBuilder,
        input_feature_name: str,
        target_feature_name: str,
        input_feature_spec: FeatureSpec,
        target_feature_spec: FeatureSpec,
        data_loader: DataLoader = None,
    ):
        """Adds an objectdetection model to the graph spec builder

        Arguments:
            graph_spec_builder: the entity used to construct the final graph
            input_feature_name: name of the input feature
            target_feature_name: name of the target feature
            input_feature_spec: properties of the input feature
            target_feature_spec: properties of the target feature
        """

        id1 = builder.add_layer(
            "IoInput",
            settings={
                "name": input_feature_name,
                "feature_name": input_feature_name,
                "datatype": input_feature_spec.datatype,
            },
        )
        id2 = builder.add_layer("LayerObjectDetectionModel", settings={})
        id3 = builder.add_layer(
            "IoOutput",
            settings={
                "name": target_feature_name,
                "feature_name": target_feature_name,
                "datatype": target_feature_spec.datatype,
            },
        )

        builder.add_connection(id1, "output", id2, "input")
        builder.add_connection(id2, "output", id3, "input")
        return
