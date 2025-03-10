import pytest
from perceptilabs.automation.modelrecommender import ModelRecommender
from perceptilabs.data.settings import FeatureSpec
from unittest.mock import MagicMock


def test_single_numerical_input_and_output_gives_basic_network():
    feature_specs = {
        "x1": FeatureSpec(datatype="numerical", iotype="input"),
        "y1": FeatureSpec(datatype="numerical", iotype="target"),
    }

    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    ordered_layers = graph_spec.get_ordered_layers()

    first = ordered_layers[0]
    last = ordered_layers[-1]

    assert first.is_input_layer and first.feature_name == "x1"
    assert last.is_target_layer and last.feature_name == "y1"
    assert len(ordered_layers) > 2  # must have some form of encoder/decoder


def test_image_input_and_numerical_output_gives_basic_network():
    feature_specs = {
        "x1": FeatureSpec(datatype="numerical", iotype="input"),
        "y1": FeatureSpec(datatype="numerical", iotype="target"),
    }
    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)
    ordered_layers = graph_spec.get_ordered_layers()
    first = ordered_layers[0]
    last = ordered_layers[-1]
    assert first.is_input_layer and first.feature_name == "x1"
    assert last.is_target_layer and last.feature_name == "y1"


def test_image_input_and_boundingbox_output_gives_basic_network():
    feature_specs = {
        "x1": FeatureSpec(datatype="image", iotype="input"),
        "y1": FeatureSpec(datatype="boundingbox", iotype="target"),
    }
    data_loader = MagicMock()
    recommender = ModelRecommender(data_loader)
    graph_spec = recommender.get_graph(feature_specs)
    ordered_layers = graph_spec.get_ordered_layers()
    first = ordered_layers[0]
    last = ordered_layers[-1]
    assert first.is_input_layer and first.feature_name == "x1"
    assert last.is_target_layer and last.feature_name == "y1"


def test_multi_inputs():
    feature_specs = {
        "x1": FeatureSpec(datatype="numerical", iotype="input"),
        "x2": FeatureSpec(datatype="numerical", iotype="input"),
        "x3": FeatureSpec(datatype="numerical", iotype="input"),
        "y1": FeatureSpec(datatype="numerical", iotype="target"),
    }
    recommender = ModelRecommender()
    graph_spec = recommender.get_graph(feature_specs)

    num_inputs_to_first_merge = None
    for layer_spec in graph_spec.get_ordered_layers():
        if layer_spec.type_ == "MathMerge":
            num_inputs_to_first_merge = len(layer_spec.input_connections)
            break

    assert num_inputs_to_first_merge == 3
