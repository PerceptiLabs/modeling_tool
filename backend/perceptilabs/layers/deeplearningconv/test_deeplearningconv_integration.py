import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningconv.spec import DeepLearningConvSpec
from perceptilabs.layers.specbase import LayerConnection


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_conv2d_1x1_should_be_sum(script_factory):
    """ Inspired from answer in: https://datascience.stackexchange.com/questions/6107/what-are-deconvolutional-layers """
    
    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation=None,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = np.ones((1, 2, 2, 1), dtype=np.float32)    

    inputs = {'input': tf.constant(x)}
    outputs = layer(inputs)
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        w = sess.run(next(iter(layer.weights.values())))
        b = sess.run(next(iter(layer.biases.values())))

        output_values = sess.run(outputs)
        
    actual = output_values['output']
    expected = np.sum(w) + b
    
    assert (expected.squeeze() == actual.squeeze()).all()
    

def test_conv2d_zero_keep_prob_equals_zero_output(script_factory):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation=None,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = np.ones((1, 2, 2, 1), dtype=np.float32)        
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


def test_conv2d_is_training_overrides_dropout(script_factory):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation=None,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = np.ones((1, 2, 2, 1), dtype=np.float32)        
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


    
