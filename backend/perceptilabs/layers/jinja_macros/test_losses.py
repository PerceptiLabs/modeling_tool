import pytest
import numpy as np
import tensorflow as tf


def test_weighted_crossentropy_output(load_jinja_macro):
    class_weights = 1.0

    module = load_jinja_macro(
        'losses.j2',
        'loss_weighted_crossentropy',
        macro_parameters={
            'declared_name': 'loss_fn',
            'class_weights': class_weights
        },
        preamble='import tensorflow as tf'
    )

    y_true = tf.constant([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])

    y_pred = tf.constant([
        [0.6, 0.0, 0.3],
        [0.6, 0.7, 0.3],
        [0.6, 0.0, 0.3]
    ])
    weights = tf.constant(class_weights)

    # Compute the expected value using the derivation from
    # https://www.tensorflow.org/api_docs/python/tf/nn/weighted_cross_entropy_with_logits
    x = y_pred
    z = y_true
    q = weights
    l = (1 + (q - 1) * z)
    e = (1 - z) * x + l * (tf.math.log(1 +
                                       tf.math.exp(-tf.math.abs(x))) + tf.math.maximum(-x, 0))

    expected = np.mean(e.numpy())
    actual = module.loss_fn(y_true, y_pred).numpy()

    assert np.isclose(actual, expected)


def test_dice_output(load_jinja_macro):
    module = load_jinja_macro(
        'losses.j2',
        'loss_dice',
        macro_parameters={
            'declared_name': 'loss_fn'
        },
        preamble='import tensorflow as tf'
    )

    y_true = tf.constant([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])

    y_pred = tf.constant([
        [0.6, 0.0, 0.3],
        [0.6, 0.7, 0.3],
        [0.6, 0.0, 0.3]
    ])

    eps = 1e-5
    intersection = tf.reduce_sum(tf.multiply(y_pred, y_true))
    union = eps + tf.reduce_sum(tf.multiply(y_pred, y_pred)) + \
        tf.reduce_sum(tf.multiply(y_true, y_true))
    cost_tmp = (2 * intersection + eps)/union
    cost_clip = tf.clip_by_value(cost_tmp, eps, 1.0-eps)
    loss_tensor = 1 - cost_clip
    expected = loss_tensor.numpy()
    actual = module.loss_fn(y_true, y_pred).numpy()

    assert np.isclose(actual, expected)
