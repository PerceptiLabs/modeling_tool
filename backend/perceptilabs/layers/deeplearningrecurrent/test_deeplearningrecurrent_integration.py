import pytest

import tensorflow as tf
import tensorflow.keras.backend as K
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningrecurrent.spec import DeepLearningRecurrentSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


@pytest.mark.pre_datawizard    
def test_basics(script_factory):
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    z = layer({'input': x})    

    with tf.compat.v1.Session() as sess:
        sess.run(tf.compat.v1.global_variables_initializer())
        output = sess.run(z)
    
    
    assert output['output'].shape == (16, 7)

    
def test_basics_tf2x(script_factory_tf2x):
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        activation='LeakyReLU',
        version='RNN',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3)).astype(np.float32)) # [batch, time, features]

    z = layer({'input': x})    
    
    assert z['output'].shape == (16, 7)

