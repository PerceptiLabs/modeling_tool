import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import NumericalPipelineBuilder


def test_numerical_postprocessing():
    expected = [1.0, 2.0, 3.0]
    
    dataset = tf.data.Dataset.from_tensor_slices([int(x) for x in expected])  # Convert to ints
    pipeline, _, _ = NumericalPipelineBuilder().build()
    processed_dataset = dataset.map(lambda x: pipeline(x))

    actual = [x.numpy() for x in iter(processed_dataset)]
    assert actual == expected


def test_numerical_normalization():
    n_samples = 10
    dataset = tf.data.Dataset.from_tensor_slices([i for i in range(n_samples)])

    feature_spec = MagicMock()
    feature_spec.preprocessing = {'normalize': True}
    
    pipeline, _, _ = NumericalPipelineBuilder().build(feature_spec=feature_spec, feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    batch = next(iter(processed_dataset.batch(n_samples))).numpy()  # Get the full dataset in a batch

    assert np.isclose(batch.mean(), 0, atol=1e-05)
    assert np.isclose(batch.std(), 1, atol=1e-05)
    
