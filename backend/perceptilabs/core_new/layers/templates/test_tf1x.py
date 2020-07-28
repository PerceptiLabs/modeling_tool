import numpy as np
import tensorflow as tf
import pkg_resources
import pytest


import perceptilabs.core_new.layers.templates.utils as utils
from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer, render_macro
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE, TOP_LEVEL_IMPORTS, TOP_LEVEL_IMPORTS_FLAT

@pytest.fixture(autouse=True)
def reset():
    yield
    tf.reset_default_graph()

    
@pytest.fixture(scope='module')
def j2_engine():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory)
    yield j2_engine


@pytest.fixture(scope='function')    
def sess():
    yield tf.Session()

    
def test_grayscale_8x8x3_to_8x8x1(j2_engine, sess):
    layer = create_layer(j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,  layer_type='ProcessGrayscale')

    x = tf.constant(np.random.random((8, 8, 3)))
    y = layer(x)
    assert y.shape == (8, 8, 1)


def test_reshape_9x1_to_3x3(j2_engine, sess):
    layer = utils.run_and_get_layer_macro(
        j2_engine, DEFINITION_TABLE,
        'tf1x.j2', 'layer_tf1x_reshape',
        'ProcessReshape',
        {'shape': (3, 3), 'permutation': (0, 1)},
        import_statements=TOP_LEVEL_IMPORTS_FLAT
    )
    
    x = tf.constant(np.random.random((1, 9, 1)))
    y = layer(x)
    assert y.shape == (1, 3, 3)

    
def test_reshape_27x1_to_3x3x3(j2_engine, sess):
    layer = utils.run_and_get_layer_macro(
        j2_engine, DEFINITION_TABLE,
        'tf1x.j2', 'layer_tf1x_reshape',
        'ProcessReshape',
        {'shape': (3, 3, 3), 'permutation': (0, 1, 2)},
        import_statements=TOP_LEVEL_IMPORTS_FLAT
    )

    x = tf.constant(np.random.random((1, 27, 1)))
    y = layer(x)
    assert y.shape == (1, 3, 3, 3)

def test_image_reshape_10x1_to_256x256(j2_engine, sess):
    layer = create_layer(j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,  layer_type='ProcessRescale', 
                        width = 256, height = 256)
    x = tf.constant(np.random.random((1,10,1)))

    y = layer(x)
    assert y.shape == (256,256,1)

def test_image_reshape_300x1_to_16x16(j2_engine, sess):
    layer = create_layer(j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,  layer_type='ProcessRescale', 
                        width = 16, height = 16)
    x = tf.constant(np.random.random((1,300,1)))

    y = layer(x)
    assert y.shape == (16,16,1)

    
def test_fully_connected_1x1_should_be_normal_multiplication(j2_engine, sess):
    layer = create_layer(j2_engine,
                         DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
                         layer_type='DeepLearningFC',
                         n_neurons=1,
                         activation='tf.compat.v1.sigmoid',
                         dropout=False, keep_prob=1.0,
                         batch_norm=False)

    x = 32*np.ones((1, 1))
    y = layer(tf.constant(x))

    sess.run(tf.global_variables_initializer())
    w = sess.run(next(iter(layer.weights.values())))
    b = sess.run(next(iter(layer.biases.values())))
    sigmoid = lambda x: 1/(1+np.exp(-x))
    y_ = sigmoid(w*x + b)
    
    assert np.isclose(sess.run(y), y_)

    
def test_conv2d_1x1_should_be_sum(j2_engine, sess):
    layer = create_layer(
        j2_engine,
        DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT, 
        layer_type='DeepLearningConv',
        conv_dim='2D',
        patch_size=2,
        padding='VALID',
        feature_maps=1,
        stride=1,
        activation=None,
        dropout=False,
        keep_prob=1,
        batch_norm=False,
        pool=False,
        pooling=None,
        pool_area=None,
        pool_stride=None
    )
                         
    x = np.ones((1, 2, 2, 1), dtype=np.float32)
    y = layer(tf.constant(x))

    sess.run(tf.global_variables_initializer())

    w = sess.run(next(iter(layer.weights.values())))
    b = sess.run(next(iter(layer.biases.values())))
    y_ = np.sum(w) + b 
    
    assert np.isclose(sess.run(y), y_)

    
def test_one_hot_sum_of_output_equals_number_of_samples(j2_engine, sess):
    n_classes = 3
    layer = create_layer(j2_engine, DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,  layer_type='ProcessOneHot', n_classes=n_classes)

    x = np.array([[x+1] for x in range(n_classes)])
    y = layer(tf.constant(x))    

    y = np.sum(sess.run(y))
    y_ = len(x) - 1
    assert y == y_
    

