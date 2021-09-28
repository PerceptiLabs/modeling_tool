import pytest
import numpy as np
from perceptilabs.layers.pretrainedmobilenetv2.stats import MobileNetV2OutputStats



def test_stats_objects_are_equal_when_args_are_equal():
    outputs1 = np.array([0.5,0.4])
    weights1 = np.array([-0.3,0.9])
    bias1 = np.array([0.43])
    gradients1 = np.array([0.2,0.7])
    obj1 = MobileNetV2OutputStats(weights1, bias1, outputs1, gradients1)

    outputs2 = np.array([0.5,0.4])
    weights2 = np.array([-0.3,0.9])
    bias2 = np.array([0.43])
    gradients2 = np.array([0.2,0.7])
    obj2 = MobileNetV2OutputStats(weights2, bias2, outputs2, gradients2)

    outputs3 = np.array([0.4,0.4])
    weights3 = np.array([-0.2,0.9])
    bias3 = np.array([0.43])
    gradients3 = np.array([0.2,0.7])
    obj3 = MobileNetV2OutputStats(weights3, bias3, outputs3, gradients3)
    assert obj1 == obj2 != obj3
