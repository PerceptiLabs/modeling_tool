import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.pretrainedinceptionv3.spec import PreTrainedInceptionV3Spec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

@pytest.mark.tf2x
def test_inceptionv3_instantiation(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        weights='None',
        trainable=False
    )

    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    assert layer is not None


@pytest.mark.tf2x
def test_inceptionv3_can_run(script_factory_tf2x):
    layer_spec = PreTrainedInceptionV3Spec(
        id_='layer_id',
        name='layer_name',
        include_top=False,
        trainable=False,
        weights='None',
        backward_connections=(LayerConnection(dst_var='input'),)     
    )

    input_data = np.random.random((100,85,85,3)) # [batch, time, features]
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory_tf2x, layer_spec).get_instance()
    y = layer({'input': x})
    assert y['output'].shape == (100, 1, 1, 2048)
    