import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathsoftmax.spec import MathSoftmaxSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_softmax(script_factory):
    layer_spec = MathSoftmaxSpec(
        id_='layer_id',
        name='layer_name',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()


    x = np.array([0., -1., 2., 3.])

    y = layer({'input': tf.constant(x)})    

    with tf.Session() as sess:        
        actual = sess.run(y)['output']

    expected = np.array([0.03467109, 0.01275478, 0.25618663, 0.69638747])
    assert np.allclose(actual, expected)

