import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.pretrainedinceptionv3.spec import PreTrainedInceptionV3Spec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
def test_inceptionv3_instantiation(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        weights='None',
        trainable=False
    )

    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    assert layer is not None


def test_inceptionv3_can_run(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)     
    )

    input_data = np.random.random((10,224,224,3)) # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y = layer({'input': x})
    assert y['output'].shape == (10, 5, 5, 2048)
    

def test_inceptionv3_output_changes_in_training_mode_with_training_argument(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=True,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))  # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() != y2['output'].numpy()).any()
    

def test_inceptionv3_output_doesnot_change_in_inference_mode_with_training_argument(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    input_data = np.random.random((1, 224, 224, 3))  # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y1 = layer({'input': x}, training=False)
    y2 = layer({'input': x}, training=True)
    assert (y1['output'].numpy() == y2['output'].numpy()).all()



