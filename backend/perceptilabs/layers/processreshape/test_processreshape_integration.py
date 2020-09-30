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
    


