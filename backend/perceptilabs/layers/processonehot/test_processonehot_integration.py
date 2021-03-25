import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.mark.pre_datawizard
def test_one_hot_sum_of_output_equals_number_of_samples(script_factory):
    n_classes = 3
    
    layer_spec = ProcessOneHotSpec(
        id_='layer_id',
        name='layer_name',
        n_classes=n_classes,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()


    x = np.array([[x+1] for x in range(n_classes)])
    y = layer({'input': tf.constant(x)})    

    with tf.compat.v1.Session() as sess:        
        actual = np.sum(sess.run(y)['output'])
        
    expected = len(x) - 1
    assert actual == expected


def test_tf2x_one_hot_sum_of_output_equals_number_of_samples(script_factory_tf2x):
    n_classes = 3
    
    layer_spec = ProcessOneHotSpec(
        id_='layer_id',
        name='layer_name',
        n_classes=n_classes,
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()


    x = np.array([[x+1] for x in range(n_classes)])
    y = layer({'input': x})
    
    actual = np.sum(y['output'].numpy())
    expected = len(x) - 1
    assert actual == expected

