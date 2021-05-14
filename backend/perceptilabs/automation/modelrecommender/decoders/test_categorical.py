import pytest
from unittest.mock import MagicMock

from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.automation.modelrecommender.decoders import CategoricalDecoderBlueprint


def test_decoder_shape_reflects_num_categories():
    expected = 123
    
    builder = GraphSpecBuilder()

    preprocessing = MagicMock()
    preprocessing.n_categories = expected
    
    data_loader = MagicMock()
    data_loader.get_preprocessing_pipeline.return_value = preprocessing

    feature_spec = MagicMock()
    feature_spec.datatype = 'categorical'
    feature_spec.file_path = '/tmp/tmp.csv'    
    
    blueprint = CategoricalDecoderBlueprint()
    blueprint.build(
        builder,
        feature_name='abc',
        feature_spec=feature_spec,
        data_loader=data_loader
    )

    graph_spec = builder.build()    

    for layer_spec in graph_spec.get_predecessors(graph_spec.target_layers[0]):
        assert layer_spec.n_neurons == expected
