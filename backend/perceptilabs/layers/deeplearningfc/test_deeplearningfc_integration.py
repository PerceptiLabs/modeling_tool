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


def test_fully_connected_zero_keep_prob_equals_zero_output(script_factory):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=True,
        keep_prob=1e-7
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = 32*np.ones((10, 10))
    y = layer({'input': tf.constant(x)})


    # To rule out chance: evaluate the layer several times and assert outputs are zero on average
    n_fails = 0
    n_trials = 50
    for i in range(n_trials):
        with tf.Session() as sess:    
            sess.run(tf.global_variables_initializer())
            output = sess.run(y)['output']

            if np.any(output != 0):
                n_fails += 1

    assert n_fails/n_trials < 1/50 # Allow 1/50 to be a failure


def test_fully_connected_is_training_overrides_dropout(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=True,
        keep_prob=1e-7
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = 32*np.ones((10, 10))
    y = layer({'input': tf.constant(x)}, is_training=tf.constant(False))


    # To rule out chance: evaluate the layer several times and assert outputs are non-zero on average
    n_fails = 0
    n_trials = 50
    for i in range(n_trials):
        with tf.Session() as sess:    
            sess.run(tf.global_variables_initializer())
            output = sess.run(y)['output']

            if np.all(output == 0):
                n_fails += 1

    assert n_fails/n_trials < 1/50 # Allow 1/50 to be a failure
