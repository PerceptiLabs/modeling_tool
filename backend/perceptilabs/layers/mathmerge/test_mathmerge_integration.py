import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathmerge.spec import MathMergeSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_concat_vertically(script_factory):
    layer_spec = MathMergeSpec(
        id_='layer_id',
        name='layer_name',
        merge_type='Concat',
        merge_dim=1
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3)))
    y = tf.constant(np.random.random((16, 12, 3)))

    z = layer({'input1': x, 'input2': y})    

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        output = sess.run(z)
    
    assert output['output'].shape == (16, 22, 3)

