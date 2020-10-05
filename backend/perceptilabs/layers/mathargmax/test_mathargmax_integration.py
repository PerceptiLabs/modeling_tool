import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathargmax.spec import MathArgmaxSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_argmax(script_factory):
    layer_spec = MathArgmaxSpec(
        id_='layer_id',
        name='layer_name',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()


    x = np.array([0., -1., 3., 0.])

    y = layer({'input': tf.constant(x)})    

    with tf.Session() as sess:        
        actual = sess.run(y)['output']
    
    expected = 2
    assert actual == expected

