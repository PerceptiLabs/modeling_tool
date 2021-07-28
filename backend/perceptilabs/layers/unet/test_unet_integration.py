import pytest

import numpy as np
import tensorflow as tf

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.unet.spec import UNetSpec
from perceptilabs.layers.specbase import LayerConnection

@pytest.fixture(scope='function', params=[None,'VGG16'])
def unet_spec(request):
    layer_spec = UNetSpec(
        type_ = 'UNet',
        filter_num = [64, 128, 256, 512],
        n_labels = 1,
        stack_num_down = 2,
        stack_num_up = 2,
        activation = 'ReLU',
        output_activation = None,
        batch_norm = False,
        pool = 'max',
        unpool = 'bilinear',
        backbone = request.param,
        weights = 'imagenet',
        freeze_backbone = True,
        freeze_batch_norm = True,
        name = 'UNet',
        backward_connections=(LayerConnection(dst_var='input'),)
    )
    yield layer_spec


def test_unet_instantiation(unet_spec, script_factory):
    layer = LayerHelper(script_factory, unet_spec).get_instance()
    assert layer is not None

def test_unet_can_run(unet_spec, script_factory):
    input_data = np.random.random((10, 224, 224, 3))
    x = tf.cast(input_data, tf.float32)
    layer = LayerHelper(script_factory, unet_spec).get_instance()
    y = layer({'input': x})

    assert y['output'].shape == (10, 224, 224, 1)
