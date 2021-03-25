import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_reshape_9x1_to_3x3(script_factory):
    layer_spec = ProcessReshapeSpec(
        id_='layer_id',
        name='layer_name',
        shape=(3, 3),
        permutation=(0, 1),
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = tf.constant(np.random.random((1, 9, 1)))
    y = layer({'input': x})
    assert y['output'].shape == (1, 3, 3)
    

def test_reshape_27x1_to_3x3x3(script_factory):
    layer_spec = ProcessReshapeSpec(
        id_='layer_id',
        name='layer_name',
        shape=(3, 3, 3),
        permutation=(0, 1, 2),
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()

    x = tf.constant(np.random.random((1, 27, 1)))
    y = layer({'input': x})
    assert y['output'].shape == (1, 3, 3, 3)
    

@pytest.mark.tf2x
def test_tf2x_reshape_9x1_to_3x3(script_factory_tf2x):
    layer_spec = ProcessReshapeSpec(
        id_='layer_id',
        name='layer_name',
        shape=(3, 3),
        permutation=(0, 1),
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance(print_code=True)

    x = np.random.random((1, 9, 1))
    y = layer({'input': x})
    assert y['output'].shape == (1, 3, 3)

    
def test_tf2x_reshape_27x1_to_3x3x3(script_factory_tf2x):
    layer_spec = ProcessReshapeSpec(
        id_='layer_id',
        name='layer_name',
        shape=(3, 3, 3),
        permutation=(0, 1, 2),
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = np.random.random((1, 27, 1))
    y = layer({'input': x})
    assert y['output'].shape == (1, 3, 3, 3)
    

def test_tf2x_reshape_784_to_28x28x0_equals_28x28(script_factory_tf2x):
    layer_spec = ProcessReshapeSpec(
        id_='layer_id',
        name='layer_name',
        shape=(28, 28, 0),
        permutation=(0, 1, 2),
        backward_connections=(LayerConnection(dst_var='input'),)        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()

    x = np.random.random((1, 784))
    y = layer({'input': x})
    assert y['output'].shape == (1, 28, 28)

