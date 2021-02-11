import pytest
from perceptilabs.modelrecommender import ModelRecommender, FeatureSpec


@pytest.mark.tf2x    
def test_single_numerical_input_and_output_gives_basic_network():
    feature_specs={
        'x1': FeatureSpec('numerical', 'input', 'data.csv'),
        'y1': FeatureSpec('numerical', 'output', 'data.csv'),
    }

    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    ordered_layers = graph_spec.get_ordered_layers()

    first = ordered_layers[0]
    last = ordered_layers[-1]    

    assert first.is_input_layer and first.feature_name == 'x1' and first.file_path == 'data.csv'
    assert last.is_output_layer and last.feature_name == 'y1' and last.file_path == 'data.csv'    
    assert len(ordered_layers) > 2 # must have some form of encoder/decoder
    


    
    
