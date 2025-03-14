import pytest
import tensorflow as tf
import numpy as np

from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.mathmerge.spec import MathMergeSpec
from perceptilabs.layers.specbase import LayerConnection


@pytest.fixture(scope="module")
def script_factory():
    yield ScriptFactory()


def test_tf2x_concat_horizontally(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Concat",
        merge_dim=0,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3)))
    y = tf.constant(np.random.random((16, 10, 3)))
    z = layer({"input1": x, "input2": y})

    assert z["output"].shape == (32, 10, 3)


def test_tf2x_concat_horizontally_with_3_inputs(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Concat",
        merge_dim=0,
        input_count=3,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
            LayerConnection(dst_var="input3"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((12, 10, 3)))
    y = tf.constant(np.random.random((14, 10, 3)))
    z = tf.constant(np.random.random((16, 10, 3)))
    w = layer({"input1": x, "input2": y, "input3": z})

    assert w["output"].shape == (12 + 14 + 16, 10, 3)


def test_tf2x_concat_vertically(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Concat",
        merge_dim=1,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.random((16, 10, 3)))
    y = tf.constant(np.random.random((16, 12, 3)))
    z = layer({"input1": x, "input2": y})

    assert z["output"].shape == (16, 22, 3)


def test_tf2x_merge_add(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Add",
        merge_dim=1,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    y = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    z = layer({"input1": x, "input2": y})

    expected = tf.add(x, y)

    assert z["output"].shape == (16, 10, 3)
    assert np.isclose(z["output"], expected).all()


def test_tf2x_merge_subtract(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Sub",
        merge_dim=1,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    y = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    z = layer({"input1": x, "input2": y})

    expected = tf.subtract(x, y)

    assert z["output"].shape == (16, 10, 3)
    assert np.isclose(z["output"], expected).all()


def test_tf2x_merge_multiply(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Multi",
        merge_dim=1,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    y = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    z = layer({"input1": x, "input2": y})

    expected = tf.multiply(x, y)

    assert z["output"].shape == (16, 10, 3)
    assert np.isclose(z["output"], expected).all()


def test_tf2x_merge_divide(script_factory):
    layer_spec = MathMergeSpec(
        id_="layer_id",
        name="layer_name",
        merge_type="Div",
        merge_dim=1,
        backward_connections=(
            LayerConnection(dst_var="input1"),
            LayerConnection(dst_var="input2"),
        ),
    )

    layer = LayerHelper(script_factory, layer_spec).get_instance()
    x = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    y = tf.constant(np.random.randint(1, 10, (16, 10, 3)))
    z = layer({"input1": x, "input2": y})

    expected = tf.divide(x, y)

    assert z["output"].shape == (16, 10, 3)
    assert np.isclose(z["output"], expected).all()
