import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningdeconv.spec import DeepLearningDeconvSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_basics(script_factory):
    """ Inspired from answer in: https://datascience.stackexchange.com/questions/6107/what-are-deconvolutional-layers """
    
    layer_spec = DeepLearningDeconvSpec(
        id_='layer_id',
        name='layer_name',
        padding='SAME',
        stride=2,
        feature_maps=1,
        activation=None
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    # input batch shape = (1, 2, 2, 1) -> (batch_size, height, width, channels) - 2x2x1 image in batch of 1
    x = tf.constant(np.array([[
        [[1], [2]], 
        [[3], [4]]
    ]]), tf.float32)

    # shape = (3, 3, 1, 1) -> (height, width, input_channels, output_channels) - 3x3x1 filter
    w_value = tf.constant(np.array([
        [[[1]], [[1]], [[1]]], 
        [[[1]], [[1]], [[1]]], 
        [[[1]], [[1]], [[1]]]
    ]), tf.float32)

    b_value = tf.constant(np.array([1]), tf.float32)
    

    output_tensor = layer({'input': x})
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        
        w_tensor = next(iter(layer.weights.values()))
        b_tensor = next(iter(layer.biases.values()))
        sess.run(w_tensor.assign(w_value))
        sess.run(b_tensor.assign(b_value))
        
        output = sess.run(output_tensor)
        
    actual = output['output']
    
    expected = np.array([[
        [[1.0], [1.0],  [3.0], [2.0]],
        [[1.0], [1.0],  [3.0], [2.0]],
        [[4.0], [4.0], [10.0], [6.0]],
        [[3.0], [3.0],  [7.0], [4.0]]]
    ])
    
    assert (expected == actual).all()
    


def test_deconv_zero_keep_prob_equals_zero_output(script_factory):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningDeconvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation=None,
        dropout=True,
        keep_prob=1e-7
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


def test_deconv_is_training_overrides_dropout(script_factory):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningDeconvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation=None,
        dropout=True,
        keep_prob=1e-7
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


    
