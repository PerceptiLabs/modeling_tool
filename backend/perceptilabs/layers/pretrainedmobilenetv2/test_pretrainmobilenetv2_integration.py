import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.pretrainedmobilenetv2.spec import PreTrainedMobileNetV2Spec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
def test_mobilenetv2_instantiation(script_factory_tf2x):
    layer_spec = PreTrainedMobileNetV2Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        alpha=1.0,
        weights='None',
        pooling='max',
        trainable=False
    )

    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    assert layer is not None


def test_mobilenetv2_can_run(script_factory_tf2x):
    layer_spec = PreTrainedMobileNetV2Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        alpha=1.0,
        weights='None',
        trainable=False,
        backward_connections=(LayerConnection(dst_var='input'),)
    )

    input_data = np.random.random((10,224,224,3)) # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y = layer({'input': x})

    # To get this final output shape
    # please refer to research paper here: https://arxiv.org/pdf/1801.04381.pdf -- Page 5

    assert y['output'].shape == (10, 7, 7, 1280)
    

def test_mobilenetv2_output_changes_in_training_mode_with_training_argument(script_factory_tf2x):
    layer_spec = PreTrainedMobileNetV2Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        alpha=1.0,
        trainable=True,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))   # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() != y2['output'].numpy()).any()


def test_mobilenetv2_output_doesnot_change_in_inference_mode_with_training_argument(script_factory_tf2x):
    layer_spec = PreTrainedMobileNetV2Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        alpha=1.0,
        trainable=False,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))   # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() == y2['output'].numpy()).all()
