import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.pretrainedvgg16.spec import PreTrainedVGG16Spec
from perceptilabs.layers.specbase import LayerConnection

@pytest.mark.parametrize('pooling',['None', 'avg', 'max'])
def test_vgg16_instantiation(script_factory, pooling):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        weights='None',
        trainable=False,
        pooling=pooling
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    assert layer is not None

@pytest.mark.parametrize('pooling',['None', 'avg', 'max'])
def test_vgg16_can_run(script_factory, pooling):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        pooling=pooling,
        backward_connections=(LayerConnection(dst_var='input'),)     
    )

    input_data = np.random.random((10, 224, 224, 3)) # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    y = layer({'input': x})
    if pooling == 'None':
        assert y['output'].shape == (10, 7, 7, 512)
    else:
        assert y['output'].shape == (10, 512)
    
        

@pytest.mark.parametrize('pooling',['None', 'avg', 'max'])
def test_vgg16_output_doesnot_change_in_training_mode_with_training_argument(script_factory, pooling):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=True,
        weights='None',
        pooling=pooling,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))  # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() == y2['output'].numpy()).all() #vgg doesn't has dropouts

@pytest.mark.parametrize('pooling',['None', 'avg', 'max'])
def test_vgg16_output_doesnot_change_in_inference_mode_with_training_argument(script_factory, pooling):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        pooling=pooling,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))  # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() == y2['output'].numpy()).all()
