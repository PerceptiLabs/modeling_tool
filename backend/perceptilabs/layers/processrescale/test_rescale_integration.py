import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.processrescale.spec import ProcessRescaleSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_rescale_up(script_factory):
    layer_spec = ProcessRescaleSpec(
        id_='layer_id',
        name='layer_name',
        width='256',
        height='256',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((1,10,1)))
    y = layer({'input':x})
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        output = sess.run(y)
    assert y['output'].shape == (256,256,1)

def test_rescale_down(script_factory):
    layer_spec = ProcessRescaleSpec(
        id_='layer_id',
        name='layer_name',
        width='10',
        height='10',
        backward_connections=(LayerConnection(dst_var='input'),)                
    )
    
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((1,45,1)))
    y = layer({'input':x})
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        output = sess.run(y)
    assert y['output'].shape == (10,10,1)
