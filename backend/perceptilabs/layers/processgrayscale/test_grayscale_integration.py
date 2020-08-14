import pytest

import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.processgrayscale.spec import ProcessGrayscaleSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_grayscale_8x8x3_to_8x8x1(script_factory):
    layer_spec = ProcessGrayscaleSpec(
        id_='layer_id',
        name='layer_name'
    )
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((8, 8, 3)))
    y = layer({'input': x})
    assert y['output'].shape == (8, 8, 1)


    
