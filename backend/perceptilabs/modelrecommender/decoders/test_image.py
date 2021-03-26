
import pytest
from perceptilabs.modelrecommender import ModelRecommender
from perceptilabs.data.base import DataLoader, FeatureSpec
from unittest.mock import MagicMock

from perceptilabs.graph.builder import GraphSpecBuilder

from perceptilabs.modelrecommender.decoders.image import ImageDecoderBlueprint

@pytest.mark.tf2x    
def test_numerical_input_and_image_output_gives_correct_settings():
    builder = GraphSpecBuilder()

    preprocessing = MagicMock()
    preprocessing.image_shape = (28,28,3)

    data_loader = MagicMock()
    data_loader.get_preprocessing_pipeline.return_value = preprocessing

    expected_conv_type = 'Transpose'
    expected_shape = preprocessing.image_shape[-1]
    feature_spec = MagicMock()
    feature_spec.datatype = 'image'
    feature_spec.file_path = '/tmp/tmp.csv'    
    
    blueprint = ImageDecoderBlueprint()
    blueprint.build(
        builder,
        feature_name='abc',
        feature_spec=feature_spec,
        data_loader=data_loader
    )

    graph_spec = builder.build()    

    for layer_spec in graph_spec.get_predecessors(graph_spec.output_layers[0]):
        assert layer_spec.conv_type == expected_conv_type
        assert layer_spec.feature_maps == expected_shape