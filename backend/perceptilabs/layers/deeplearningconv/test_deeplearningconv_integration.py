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

    with tf.Session() as sess:    
        sess.run(tf.global_variables_initializer())
        output = sess.run(y)['output']
        assert np.allclose(output, 0)
    

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

    with tf.Session() as sess:    
        sess.run(tf.global_variables_initializer())
        output = sess.run(y)['output']
        assert not np.allclose(output, 0)



@pytest.mark.tf2x
def test_tf2x_conv2d_1x1_should_be_sum(script_factory_tf2x):
    """ Inspired from answer in: https://datascience.stackexchange.com/questions/6107/what-are-deconvolutional-layers """
    
    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation='None',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)
    x = np.ones((1, 2, 2, 1), dtype=np.float32)    

    y = layer({'input': x})

    w = next(iter(layer.weights.values())).numpy()
    b = next(iter(layer.biases.values())).numpy()

    actual = y['output'].numpy()
    expected = np.sum(w) + b
    
    assert (expected.squeeze() == actual.squeeze()).all()

    
@pytest.mark.tf2x
def test_tf2x_conv2d_zero_keep_prob_equals_zero_output(script_factory_tf2x):
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
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = np.ones((1, 2, 2, 1), dtype=np.float32)        
    y = layer({'input': x})

    output = y['output'].numpy()
    assert np.allclose(output, 0)

    
@pytest.mark.tf2x
def test_tf2x_conv2d_is_training_overrides_dropout(script_factory_tf2x):
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
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = np.ones((1, 2, 2, 1), dtype=np.float32)        
    y = layer({'input': x}, training=False)

    output = y['output'].numpy()
    assert not np.allclose(output, 0)


@pytest.mark.tf2x
def test_tf2x_conv2d_batch_norm_gives_zero_mean_unit_variance(script_factory_tf2x):
    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='VALID',
        stride=2,
        patch_size=2,
        feature_maps=1,
        activation='None',
        batch_norm=True,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)
    np.random.seed(0)
    x = np.random.random((4, 2, 2, 3)).astype(np.float32)

    y = layer({'input': x})
    output = y['output'].numpy()

    assert np.isclose(np.mean(output), 0, atol=0.1) # -0.1 <= mean < 0.1
    assert np.isclose(np.var(output), 1, atol=0.1) # 0.9 <= var < 1.1


@pytest.mark.tf2x
def test_tf2x_conv2d_max_pooling_shape_ok(script_factory_tf2x):
    pool_size = 2
    stride = 3
    
    layer_spec = DeepLearningConvSpec(
        id_='layer_id',
        name='layer_name',
        padding='SAME',
        stride=1,
        patch_size=1,
        feature_maps=1,
        pool=True,
        pooling='Max',
        pool_padding='VALID',
        pool_area=pool_size,
        pool_stride=stride,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)
    np.random.seed(0)

    input_size = 10
    input_shape = (4, input_size, input_size, 1) # The layer is configured so that the dimension is preserved through the conv operation
    x = np.random.random(input_shape).astype(np.float32)

    y = layer({'input': x})
    output = y['output'].numpy()
    actual_shape = output.shape
    
    expected_shape = (
        4,
        (input_size - pool_size + 1)/stride,
        (input_size - pool_size + 1)/stride,        
        1
    )  # Taken from https://keras.io/api/layers/pooling_layers/max_pooling2d/
    
    assert actual_shape == expected_shape


    
