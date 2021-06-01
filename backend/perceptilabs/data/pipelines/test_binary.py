import pytest
import tensorflow as tf


from perceptilabs.data.pipelines import BinaryPipelineBuilder


def test_numerical_postprocessing():
    expected = [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
    
    dataset = tf.data.Dataset.from_tensor_slices([int(x) for x in expected])  # Convert to ints
    pipeline, _, _ = BinaryPipelineBuilder().build()
    processed_dataset = dataset.map(lambda x: pipeline(x))

    actual = [x.numpy() for x in iter(processed_dataset)]
    assert actual == expected
