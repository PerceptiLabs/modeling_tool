import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_one_hot_sum_of_output_equals_number_of_samples(script_factory):
    n_classes = 3
    
    layer_spec = ProcessOneHotSpec(
        id_='layer_id',
        name='layer_name',
        n_classes=n_classes
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()


    x = np.array([[x+1] for x in range(n_classes)])
    y = layer({'input': tf.constant(x)})    

    with tf.Session() as sess:        
        actual = np.sum(sess.run(y)['output'])
        
    expected = len(x) - 1
    assert actual == expected

