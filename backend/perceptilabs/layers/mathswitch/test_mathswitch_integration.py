import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathswitch.spec import MathSwitchSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_mathswitch_basic(script_factory):
    layer_spec = MathSwitchSpec(
        id_='layer_id',
        name='layer_name',
        selected_var_name='input2'
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((8, 8, 3)))
    y = tf.constant(np.random.random((9, 9, 4)))
    
    z = layer({'input1': x, 'input2': y})
    assert z['output'].shape == y.shape


    
