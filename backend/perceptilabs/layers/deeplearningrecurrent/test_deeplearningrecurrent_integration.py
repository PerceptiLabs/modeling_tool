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

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        output = sess.run(z)
    
    
    assert output['output'].shape == (16, 7)

    
def test_recurrent_zero_keep_prob_equals_zero_output(script_factory):
    """ If the keep probability is low the expected output should be zero """
    
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    y = layer({'input': x})    


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



def test_recurrent_is_training_overrides_dropout(script_factory):
    """ If the keep probability is low the expected output should be zero """
    
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    y = layer({'input': x}, is_training=tf.constant(False))
    
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
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    z = layer({'input': x})    
    
    assert z['output'].shape == (16, 7)


def test_recurrent_zero_keep_prob_equals_zero_output_tf2x(script_factory_tf2x):
    """ If the keep probability is low the expected output should be zero """
    
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]   

    # To rule out chance: evaluate the layer several times and assert outputs are zero on average

    # NOTE: Running the layer for TF2x in the same way we did for TF1x is very slow. For now, 
    # the number of trials is reduced. 
    n_fails = 0
    n_trials = 5
    for i in range(n_trials):
        y = layer({'input': x})  
        if np.any(K.eval(y['output']) != 0):
            n_fails += 1

    assert n_fails/n_trials < 1/5 # Allow 1/50 to be a failure
    

def test_recurrent_is_training_overrides_dropout_tf2x(script_factory_tf2x):
    """ If the keep probability is low the expected output should be zero """
    
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7,
        dropout=True,
        keep_prob=1e-7,
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    
    # To rule out chance: evaluate the layer several times and assert outputs are non-zero on average

    # NOTE: Running the layer for TF2x in the same way we did for TF1x is very slow. For now, 
    # the number of trials is reduced. 
    n_fails = 0
    n_trials = 5
    for i in range(n_trials):
        y = layer({'input': x}, training=False)
        if np.all(K.eval(y['output']) == 0):
            n_fails += 1

    assert n_fails/n_trials < 1/5
