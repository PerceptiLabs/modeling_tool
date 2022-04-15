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
            url="https://tfhub.dev/tensorflow/efficientdet/d2/1",
        )
        layer = LayerHelper(script_factory, layer_spec).get_instance()
        assert layer is not None


@pytest.mark.parametrize("trainable", [True, False])
def test_objectdetectionmodel_can_run(script_factory, trainable):
    a = MagicMock()

    def tf_test(x, training):
        dict_ = {
            "detection_boxes": np.random.randint(0, 100, (1, 100, 4)),
            "detection_classes": np.random.randint(0, 100, (1, 100)),
        }
        return dict_

    a.KerasLayer.return_value = tf_test

    with patch.dict(
        "sys.modules",
        **{
            "tensorflow_hub": a,
        }
    ):
        layer_spec = LayerObjectDetectionModelSpec(
            id_="layer_id",
            name="layer_name",
            trainable=trainable,
            url="https://tfhub.dev/tensorflow/efficientdet/d2/1",
            backward_connections=(LayerConnection(dst_var="input"),),
        )
        x = tf.cast(np.asarray([10]), tf.int8)
        layer = LayerHelper(script_factory, layer_spec).get_instance()
        y = layer({"input": x})
        assert list(y["output"][0].keys()) == ["detection_boxes", "detection_classes"]
