import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningrecurrent.spec import DeepLearningRecurrentSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_basics(script_factory):
    layer_spec = DeepLearningRecurrentSpec(
        id_='layer_id',
        name='layer_name',
        n_neurons=7
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3))) # [batch, time, features]

    z = layer({'input': x})    

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        output = sess.run(z)
    
    
    assert output['output'].shape == (16, 7)


    
