
import pytest
from perceptilabs.automation.modelrecommender import ModelRecommender
from perceptilabs.data.base import DataLoader, FeatureSpec
from unittest.mock import MagicMock

from perceptilabs.graph.builder import GraphSpecBuilder

from perceptilabs.automation.modelrecommender.decoders.mask import MaskDecoderBlueprint


def test_image_input_and_mask_output_gives_correct_settings():
    builder = GraphSpecBuilder()

    preprocessing = MagicMock()
    expected_shape = (224, 224,10)
    num_classes = 11
    preprocessing.metadata = {'image_shape': expected_shape, 'num_classes': num_classes}

    data_loader = MagicMock()
    data_loader.get_preprocessing_pipeline.return_value = preprocessing

    feature_spec = MagicMock()
    feature_spec.datatype = 'mask'
    feature_spec.file_path = '/tmp/tmp.csv'

    blueprint = MaskDecoderBlueprint()
    blueprint.build(
        builder,
        feature_name='abc',
        feature_spec=feature_spec,
        data_loader=data_loader
    )

    graph_spec = builder.build()

    for layer_spec in graph_spec.get_predecessors(graph_spec.target_layers[0]):
        assert layer_spec.feature_maps == expected_shape[-1]