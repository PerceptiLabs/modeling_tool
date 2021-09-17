from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.base import FeatureSpec, DataLoader
from perceptilabs.automation.modelrecommender.siso_models import SISOModelBlueprint
import numpy as np


class SegmentationModel(SISOModelBlueprint):
    def build(self, builder: GraphSpecBuilder, input_feature_name:str, target_feature_name:str, input_feature_spec:FeatureSpec,
                target_feature_spec:FeatureSpec, data_loader: DataLoader = None):
        """ Adds an segmentation model to the graph spec builder

        Arguments:
            graph_spec_builder: the entity used to construct the final graph
            input_feature_name: name of the input feature
            target_feature_name: name of the target feature
            input_feature_spec: properties of the input feature
            target_feature_spec: properties of the target feature
        """
        preprocessing = data_loader.get_preprocessing_pipeline(target_feature_name)
        num_classes = preprocessing.metadata['num_classes']

        id1 = builder.add_layer(
            'IoInput',
            settings={'feature_name': input_feature_name, 'file_path': input_feature_spec.file_path, 'datatype': input_feature_spec.datatype}
        )
        id2 = builder.add_layer(
            'UNet',
            settings={'n_labels':num_classes}
        )
        id3 = builder.add_layer(
            'IoOutput',
            settings={'feature_name': target_feature_name, 'file_path': target_feature_spec.file_path, 'datatype': target_feature_spec.datatype}
        )

        builder.add_connection(id1, 'output', id2, 'input')
        builder.add_connection(id2, 'output', id3, 'input')
        return