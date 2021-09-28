from perceptilabs.layers.inner_layer_stats import InnerLayersStatsTracker
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.graph.spec import GraphSpec

import numpy as np
import tensorflow as tf
import tempfile
import pytest
from unittest.mock import MagicMock

@pytest.fixture()
def graph_spec(csv_path):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1', 'file_path': csv_path, 'checkpoint_path':dirpath}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y1', 'file_path': csv_path}
    )

    # Connect the layers
    gsb.add_connection(
        source_id=id1, source_var='output',
        dest_id=id2, dest_var='input'
    )
    gsb.add_connection(
        source_id=id2, source_var='output',
        dest_id=id3, dest_var='input'
    )

    graph_spec = gsb.build()
    return graph_spec


@pytest.fixture(scope='function', params=['UNet', 'ProcessGrayscale', 'ProcessOneHot', 'MathSoftmax', 'MathArgmax', 'ProcessReshape', 'ProcessRescale', 'MathMerge', 'LayerCustom', 'PreTrainedVGG16', 'PreTrainedMobileNetV2', 'PreTrainedInceptionV3', 'PreTrainedResNet50', 'DeepLearningFC', 'DeepLearningConv', 'DeepLearningRecurrent'])
def inner_layers(request):
    layers = {'1': request.param}
    return layers
@pytest.fixture()
def outputs():
    return {
        '1': {'output': tf.constant([3.0])}
    }

@pytest.fixture()
def trainables_by_layer():
    return {
        '1': {'weights': tf.constant([3.0]), 'bias': tf.constant([12.0])}
    }

@pytest.fixture()
def gradients_by_layer():
    return {
        '1': {'weights': tf.constant([3.0]), 'bias': tf.constant([12.0])}
    }

def test_serialized_trackers_are_equal(inner_layers, outputs, trainables_by_layer, gradients_by_layer):
    tracker1 = InnerLayersStatsTracker(inner_layers)
    tracker1.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    data = tracker1.serialize()
    tracker2 = InnerLayersStatsTracker.deserialize(data)
    assert tracker1 == tracker2

def test_trackers_are_equal_when_both_are_updated(inner_layers, outputs, trainables_by_layer, gradients_by_layer):
    tracker1 = InnerLayersStatsTracker(inner_layers)
    tracker2 = InnerLayersStatsTracker(inner_layers)
    assert tracker1 == tracker2

    tracker1.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()

    tracker2.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    assert tracker1 == tracker2
    stats1 = tracker1.save()
    stats2 = tracker2.save()
    assert stats1['1'].outputs == stats2['1'].outputs


def test_layer_output_ok(inner_layers, outputs, trainables_by_layer, gradients_by_layer):
    tracker = InnerLayersStatsTracker(inner_layers)

    tracker.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)

    actual = tracker.get_layer_output('1')
    expected = np.array([3.0])
    assert np.all(actual == expected)


def test_layer_weights_is_array(inner_layers, outputs, trainables_by_layer, gradients_by_layer):

    tracker = InnerLayersStatsTracker(inner_layers)
    tracker.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    value = tracker.get_layer_weights('1')
    assert isinstance(value, np.ndarray)


def test_layer_bias_is_array(inner_layers, outputs, trainables_by_layer, gradients_by_layer):

    tracker = InnerLayersStatsTracker(inner_layers)
    tracker.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    value = tracker.get_layer_bias('1')
    assert isinstance(value, np.ndarray)


def test_layer_gradients_contain_exactly_one_float(inner_layers, outputs, trainables_by_layer, gradients_by_layer):
    tracker = InnerLayersStatsTracker(inner_layers)
    tracker.update(outputs=outputs, trainables_by_layer=trainables_by_layer, gradients_by_layer=gradients_by_layer)
    gradient_stats = tracker.gradients_tracker.save()
    gradients = tracker.get_layer_gradients('1', gradient_stats)
    minimum = gradients['Min']
    maximum = gradients['Max']
    average = gradients['Average']

    assert isinstance(minimum, list) and len(minimum) == 1 and isinstance(minimum[0], np.float32)
    assert isinstance(maximum, list) and len(maximum) == 1 and isinstance(maximum[0], np.float32)
    assert isinstance(average, list) and len(average) == 1 and isinstance(average[0], np.float32)
    assert minimum[0] <= maximum[0]
