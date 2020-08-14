import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.deeplearningconv.spec import DeepLearningConvSpec


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
        activation=None
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
    


