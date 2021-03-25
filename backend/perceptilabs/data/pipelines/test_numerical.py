import pytest
import tensorflow as tf


from perceptilabs.data.pipelines import build_numerical_pipelines


def test_numerical_postprocessing():
    expected = [1.0, 2.0, 3.0]
    
    dataset = tf.data.Dataset.from_tensor_slices([int(x) for x in expected])  # Convert to ints
    pipeline, _, _ = build_numerical_pipelines()
    processed_dataset = dataset.map(lambda x: pipeline(x))

    actual = [x.numpy() for x in iter(processed_dataset)]
    assert actual == expected
