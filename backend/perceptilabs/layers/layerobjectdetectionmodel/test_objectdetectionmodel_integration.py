import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import MagicMock, patch
import sys
import tensorflow_hub
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.layerobjectdetectionmodel.spec import (
    LayerObjectDetectionModelSpec,
)
from perceptilabs.layers.specbase import LayerConnection


@pytest.fixture(scope="module")
def script_factory():
    yield ScriptFactory()


@pytest.mark.parametrize("trainable", [True, False])
def test_objectdetectionmodel_instantiation(script_factory, trainable):
    a = MagicMock()

    def tf_test(x, training):
        x1 = tf.random.normal((1, 1, 40, 40, 64))
        x2 = tf.random.normal((1, 1, 40, 40, 64))
        return (x1, x2)

    a.KerasLayer.return_value = tf_test

    with patch.dict(
        "sys.modules",
        **{
            "tensorflow_hub": MagicMock(),
        }
    ):
        layer_spec = LayerObjectDetectionModelSpec(
            id_="layer_id",
            name="layer_name",
            trainable=trainable,
            url="https://tfhub.dev/tensorflow/efficientdet/lite3x/feature-vector/1",
        )
        layer = LayerHelper(script_factory, layer_spec).get_instance()
        assert layer is not None


@pytest.mark.parametrize("trainable", [True, False])
def test_objectdetectionmodel_can_run(script_factory, trainable):
    layer_spec = LayerObjectDetectionModelSpec(
        id_="layer_id",
        name="layer_name",
        trainable=trainable,
        url="https://tfhub.dev/tensorflow/efficientdet/lite0/feature-vector/1",
        backward_connections=(LayerConnection(dst_var="input"),),
    )
    x = tf.random.normal((1, 320, 320, 3))
    layer = LayerHelper(script_factory, layer_spec).get_instance()
    y = layer({"input": x})
    assert list(y["output"].keys()) == ["cls_outputs", "box_outputs"]
