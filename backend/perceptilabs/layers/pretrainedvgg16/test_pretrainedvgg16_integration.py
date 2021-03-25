import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.pretrainedvgg16.spec import PreTrainedVGG16Spec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
def test_vgg16_instantiation(script_factory_tf2x):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        weights='None',
        trainable=False
    )

    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    assert layer is not None


def test_vgg16_can_run(script_factory_tf2x):
    layer_spec = PreTrainedVGG16Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)     
    )

    input_data = np.random.random((100,32,32,3)) # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y = layer({'input': x})
    assert y['output'].shape == (100, 1, 1, 512)
    
