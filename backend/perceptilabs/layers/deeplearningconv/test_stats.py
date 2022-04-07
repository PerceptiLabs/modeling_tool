import pytest
import numpy as np
from perceptilabs.layers.deeplearningconv.stats import ConvPreviewStats
from perceptilabs.layers.deeplearningconv.stats import ConvOutputStats


def test_conv_preview_content_1d():
    sample = np.random.random((224, 11))
    preview_content = ConvPreviewStats().get_preview_content(sample)
    assert preview_content[1] == (224, 11)
    assert not preview_content[2]


def test_conv_preview_content_2d():
    sample = np.random.random((224, 224, 11))
    preview_content = ConvPreviewStats().get_preview_content(sample)
    assert preview_content[1] == (224, 224, 11)
    assert not preview_content[2]


def test_conv_preview_content_3d():
    sample = np.random.random((224, 224, 224, 11))
    preview_content = ConvPreviewStats().get_preview_content(sample)
    assert preview_content[1] == (224, 224, 224, 11)
    assert not preview_content[2]


def test_stats_objects_are_equal_when_args_are_equal():
    outputs1 = np.array([0.5, 0.4])
    weights1 = np.array([-0.3, 0.9])
    bias1 = np.array([0.43])
    gradients1 = np.array([0.2, 0.7])
    obj1 = ConvOutputStats(weights1, bias1, outputs1, gradients1)

    outputs2 = np.array([0.5, 0.4])
    weights2 = np.array([-0.3, 0.9])
    bias2 = np.array([0.43])
    gradients2 = np.array([0.2, 0.7])
    obj2 = ConvOutputStats(weights2, bias2, outputs2, gradients2)

    outputs3 = np.array([0.4, 0.4])
    weights3 = np.array([-0.2, 0.9])
    bias3 = np.array([0.43])
    gradients3 = np.array([0.2, 0.7])
    obj3 = ConvOutputStats(weights3, bias3, outputs3, gradients3)
    assert obj1 == obj2 != obj3
