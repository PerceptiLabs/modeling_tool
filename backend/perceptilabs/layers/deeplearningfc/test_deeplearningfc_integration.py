import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
def test_fully_connected_1x1_should_be_normal_multiplication(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid'
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})

    with tf.Session() as sess:    
        sess.run(tf.global_variables_initializer())
        w = sess.run(next(iter(layer.weights.values())))
        b = sess.run(next(iter(layer.biases.values())))

        actual = sess.run(y)['output']
        
    sigmoid = lambda x: 1/(1+np.exp(-x))
    expected = sigmoid(w*x + b)

    assert np.isclose(actual, expected)


