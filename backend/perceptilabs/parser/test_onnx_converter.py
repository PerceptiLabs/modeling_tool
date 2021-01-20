import pytest
import tensorflow as tf
from perceptilabs.parser.onnx_converter import create_onnx_from_tf1x, create_onnx_from_keras
import os

@pytest.mark.skip
def test_onnx_existence_tf2x():
    onnx_model = None

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Flatten(input_shape=(28, 28, 1)))
    model.add(tf.keras.layers.Dense(8, activation='relu'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))


    assert onnx_model is None

    onnx_model = create_onnx_from_keras(model)

    assert onnx_model is not None


def test_onnx_existence_tf1x():
    onnx_model = None
    with tf.compat.v1.Session() as sess:
        x = tf.placeholder(tf.float32, [2, 3], name="input")
        x_ = tf.add(x, x)
        _ = tf.identity(x_, name="output")

        assert onnx_model is None

        onnx_model = create_onnx_from_tf1x(sess.graph)

        assert onnx_model is not None



