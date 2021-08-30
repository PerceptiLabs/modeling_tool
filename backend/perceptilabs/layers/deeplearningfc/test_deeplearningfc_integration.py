import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.specbase import LayerConnection


@pytest.mark.parametrize("n_neurons", [1, 2])
def test_fully_connected_1x1_should_be_normal_multiplication(n_neurons, script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=n_neurons,
        activation='Sigmoid',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((n_neurons, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
        
    sigmoid = lambda x: 1/(1+np.exp(-x))
    expected = sigmoid(w*x + b)

    assert np.isclose(actual, expected).all()


def test_is_squeezed_when_num_neurons_is_one(script_factory):
    n_neurons = 1
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=n_neurons,
        activation='Sigmoid',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((n_neurons, 1))
    y = layer({'input': tf.constant(x)})
    shape = y['output'].numpy().shape
    assert n_neurons == 1
    assert shape == (1,)


@pytest.mark.parametrize("n_neurons", [1, 7])
def test_fully_connected_batch_norm_is_applied(n_neurons, script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=n_neurons,
        activation='Sigmoid',
        batch_norm=True,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.random.random((n_neurons, 1))
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
    
@pytest.mark.parametrize("n_neurons", [1, 7])
def test_fully_connected_batch_norm_uses_initial_params_when_not_training(n_neurons, script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=n_neurons,
        activation='Sigmoid',
        batch_norm=True,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.random.random((n_neurons, 1))
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
    
 
def test_fully_connected_1x1_with_no_activation(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='None',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    expected = w*x + b

    assert np.isclose(actual, expected)
   

def test_fully_connected_1x1_with_relu(script_factory):
    layer_spec = DeepLearningFcSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=1,
        activation='ReLU',
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance(print_code=True)

    x = 32*np.ones((1, 1))
    y = layer({'input': tf.constant(x)})
    
    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    expected = max(w*x + b, 0)

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
    y = layer({'input': tf.constant(x)}, training=True)

    assert np.all(y['output'] == 0)


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
    y = layer({'input': tf.constant(x)}, training=False)

    assert np.any(y['output'] != 0)    
