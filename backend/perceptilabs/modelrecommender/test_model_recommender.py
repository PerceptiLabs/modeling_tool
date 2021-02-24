import pytest
from perceptilabs.modelrecommender import ModelRecommender
from perceptilabs.data.base import FeatureSpec


@pytest.mark.tf2x    
def test_single_numerical_input_and_output_gives_basic_network():
    feature_specs={
        'x1': FeatureSpec('numerical', 'input'),
        'y1': FeatureSpec('numerical', 'output'),
    }

    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    ordered_layers = graph_spec.get_ordered_layers()

    first = ordered_layers[0]
    last = ordered_layers[-1]    

    assert first.is_input_layer and first.feature_name == 'x1' 
    assert last.is_output_layer and last.feature_name == 'y1' 
    assert len(ordered_layers) > 2 # must have some form of encoder/decoder
    

@pytest.mark.tf2x    
def test_image_input_and_numerical_output_gives_basic_network():
    feature_specs={
        'x1': FeatureSpec('image', 'input'),
        'y1': FeatureSpec('numerical', 'output'),
    }

    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    ordered_layers = graph_spec.get_ordered_layers()

    first = ordered_layers[0]
    last = ordered_layers[-1]    

    assert first.is_input_layer and first.feature_name == 'x1'
    assert last.is_output_layer and last.feature_name == 'y1'
    assert len(ordered_layers) > 2 # must have some form of encoder/decoder
    


    
    
    
