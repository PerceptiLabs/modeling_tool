import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import MagicMock, patch
import sys
import tensorflow_hub
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.layertfmodel.spec import LayerTfModelSpec
from perceptilabs.layers.specbase import LayerConnection


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

@pytest.mark.parametrize("trainable",[True, False])
def test_tfmodel_instantiation(script_factory, trainable):
    with patch.dict('sys.modules', **{ 
            'tensorflow_hub': MagicMock(),
        }):
        layer_spec = LayerTfModelSpec(
            id_='layer_id',
            name='layer_name',
            trainable=trainable, 
            url= 'https://tfhub.dev/adityakane2001/regnety200mf_classification/1',
        )
        layer = LayerHelper(script_factory, layer_spec).get_instance()
        assert layer is not None


@pytest.mark.parametrize("trainable",[True, False])
def test_tfmodel_can_run(script_factory, trainable):
    a = MagicMock()

    def tf_test(x, training):
        return tf.square(x)
        
    a.KerasLayer.return_value = tf_test
    
    with patch.dict('sys.modules', **{ 
            'tensorflow_hub': a,
        }):
        layer_spec = LayerTfModelSpec(
            id_='layer_id',
            name='layer_name',
            trainable=trainable, 
            url='https://tfhub.dev/sayakpaul/vit_s16_classification/1',
            backward_connections=(LayerConnection(dst_var='input'),)
        )
        x = tf.cast(4, tf.float32)
        layer = LayerHelper(script_factory, layer_spec).get_instance()
        y = layer({'input': x})
        assert y['output'].numpy() == np.float(16)