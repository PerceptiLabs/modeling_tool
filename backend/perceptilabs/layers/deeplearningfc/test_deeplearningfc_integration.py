import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.specbase import LayerConnection

    
def test_fully_connected_1x1_should_be_normal_multiplication(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=False,
        keep_prob=1.0,
        backward_connections=(LayerConnection(dst_var='input'),)        
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
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)                
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

    assert n_fails/n_trials <= 1/50 # Allow 1/50 to be a failure


def test_fully_connected_is_training_overrides_dropout(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)                
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = 32*np.ones((10, 10))
    y = layer({'input': tf.constant(x)}, is_training=tf.constant(False))


    # To rule out chance: evaluate the layer several times and assert outputs are non-zero on average
    with tf.Session() as sess:    
        sess.run(tf.global_variables_initializer())
        output = sess.run(y)['output']
        assert not np.allclose(output, 0)

    
@pytest.mark.tf2x                
def test_tf2x_fully_connected_1x1_should_be_normal_multiplication(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
        
    sigmoid = lambda x: 1/(1+np.exp(-x))
    expected = sigmoid(w*x + b)

    assert np.isclose(actual, expected)


@pytest.mark.tf2x                
def test_tf2x_fully_connected_batch_norm_is_applied(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        batch_norm=True,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = 32*np.random.random((10, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    linear_output = w*x + b

    # Normalize the linear output before squashing it through the activation
    mean = np.mean(linear_output, axis=0)
    variance = np.var(linear_output, axis=0)
    eps = 0.001
    normalized_linear_output = (linear_output - mean)/np.sqrt(variance + eps) # Ref: https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization
    sigmoid = lambda x: 1/(1+np.exp(-x))
    expected = sigmoid(normalized_linear_output)

    assert np.all(np.isclose(actual, expected))
    

@pytest.mark.tf2x                
def test_tf2x_fully_connected_batch_norm_uses_initial_params_when_not_training(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        batch_norm=True,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = 32*np.random.random((10, 1))
    y = layer({'input': tf.constant(x)}, training=False)
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    linear_output = w*x + b

    # Normalize the linear output before squashing it through the activation
    mean = 0 # The internal running mean is initialized to zero
    variance = 1  # The internal running mean is initialized to one
    eps = 0.001
    normalized_linear_output = (linear_output - mean)/np.sqrt(variance + eps) # Ref: https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization
    sigmoid = lambda x: 1/(1+np.exp(-x))
    expected = sigmoid(normalized_linear_output)
    
    assert np.all(np.isclose(actual, expected, rtol=1e-03))
    
 
@pytest.mark.tf2x                
def test_tf2x_fully_connected_1x1_with_no_activation(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='None',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    expected = w*x + b

    assert np.isclose(actual, expected)
   

@pytest.mark.tf2x                
def test_tf2x_fully_connected_1x1_with_relu(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='ReLU',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    expected = max(w*x + b, 0)

    assert np.isclose(actual, expected)
   
    
@pytest.mark.tf2x                
def test_tf2x_fully_connected_zero_keep_prob_equals_zero_output(script_factory_tf2x):
    """ If the keep probability is low the expected output should be zero """

    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)                
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = 32*np.ones((10, 10))
    y = layer({'input': tf.constant(x)}, training=True)

    assert np.all(y['output'] == 0)


@pytest.mark.tf2x                    
def test_tf2x_fully_connected_is_training_overrides_dropout(script_factory_tf2x):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='Sigmoid',
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)                
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = 32*np.ones((10, 10))
    y = layer({'input': tf.constant(x)}, training=False)

    assert np.any(y['output'] != 0)    
