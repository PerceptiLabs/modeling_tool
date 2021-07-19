import pytest
from perceptilabs.automation.modelrecommender import ModelRecommender
from perceptilabs.data.settings import FeatureSpec


def test_single_numerical_input_and_output_gives_basic_network():
    feature_specs={
        'x1': FeatureSpec(datatype='numerical', iotype='input', file_path=''),
        'y1': FeatureSpec(datatype='numerical', iotype='target', file_path=''),
    }

    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    ordered_layers = graph_spec.get_ordered_layers()

    first = ordered_layers[0]
    last = ordered_layers[-1]    

    assert first.is_input_layer and first.feature_name == 'x1' 
    assert last.is_target_layer and last.feature_name == 'y1' 
    assert len(ordered_layers) > 2 # must have some form of encoder/decoder
    

def test_image_input_and_numerical_output_gives_basic_network():
    feature_specs={
        'x1': FeatureSpec(datatype='numerical', iotype='input', file_path=''),
        'y1': FeatureSpec(datatype='numerical', iotype='target', file_path=''),
    }
    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)
    ordered_layers = graph_spec.get_ordered_layers()
    first = ordered_layers[0]
    last = ordered_layers[-1]    
    assert first.is_input_layer and first.feature_name == 'x1'
    assert last.is_target_layer and last.feature_name == 'y1'


    


    
    
    
