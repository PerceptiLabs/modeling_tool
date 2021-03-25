import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathswitch.spec import MathSwitchSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_mathswitch_basic(script_factory):
    layer_spec = MathSwitchSpec(
        id_='layer_id',
        name='layer_name',
        selected_var_name='input2',
        backward_connections=(
            LayerConnection(dst_var='input1'), LayerConnection(dst_var='input2')
        )        
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((8, 8, 3)))
    y = tf.constant(np.random.random((9, 9, 4)))
    
    z = layer({'input1': x, 'input2': y})
    assert z['output'].shape == y.shape

    
def test_mathswitch_basic_tf2x(script_factory_tf2x):
    layer_spec = MathSwitchSpec(
        id_='layer_id',
        name='layer_name',
        selected_var_name='input2',
        backward_connections=(
            LayerConnection(dst_var='input1'), LayerConnection(dst_var='input2')
        )        
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    x = np.random.random((8, 8, 3))
    y = np.random.random((9, 9, 4))

    z = layer({'input1': x, 'input2': y})
    assert z['output'].shape == y.shape
