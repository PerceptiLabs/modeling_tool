import os
import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import NumericalPipelineBuilder
from perceptilabs.data.settings import NumericalPreprocessingSpec


def test_normalization_without_preprocessing_is_float():
    n_samples = 10
    dataset = tf.data.Dataset.from_tensor_slices([i+2 for i in range(n_samples)])

    _, _, preprocessing_step, _ = NumericalPipelineBuilder().build_from_dataset({}, dataset)
    processed_dataset = dataset.map(lambda x: preprocessing_step(x))

    for sample1, sample2 in tf.data.Dataset.zip((dataset, processed_dataset)):
        assert sample1.numpy() == float(sample2.numpy())

def test_normalization_standardization():
    n_samples = 10
    dataset = tf.data.Dataset.from_tensor_slices([i for i in range(n_samples)])

    preprocessing = NumericalPreprocessingSpec(normalize=True, normalize_mode='standardization')
    
    _, _, pipeline, _ = NumericalPipelineBuilder().build_from_dataset(preprocessing, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    batch = next(iter(processed_dataset.batch(n_samples))).numpy()  # Get the full dataset in a batch

    assert np.isclose(batch.mean(), 0, atol=1e-05)
    assert np.isclose(batch.std(), 1, atol=1e-05)
    

def test_normalization_minmax():
    n_samples = 10
    dataset = tf.data.Dataset.from_tensor_slices([i for i in range(n_samples)])

    preprocessing = NumericalPreprocessingSpec(normalize=True, normalize_mode='min-max')    
    
    _, _, pipeline, _ = NumericalPipelineBuilder().build_from_dataset(preprocessing, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    batch = next(iter(processed_dataset.batch(n_samples))).numpy()  # Get the full dataset in a batch
    assert batch.max() == 1.0
    assert batch.min() == 0.0
    
    
def test_build_from_metadata_gives_same_results():
    n_samples = 10
    dataset = tf.data.Dataset.from_tensor_slices([i for i in range(n_samples)])

    preprocessing = NumericalPreprocessingSpec(normalize=True, normalize_mode='min-max')    
    _, _, built_pipeline, _ = NumericalPipelineBuilder().build_from_dataset(preprocessing, dataset)

    
    metadata = {'preprocessing': built_pipeline.metadata}
    _, _, loaded_pipeline, _ = NumericalPipelineBuilder().load_from_metadata(preprocessing, metadata)
    
    dataset1 = dataset.map(lambda x: built_pipeline(x))
    dataset2 = dataset.map(lambda x: loaded_pipeline(x))        

    for sample1, sample2 in tf.data.Dataset.zip((dataset1, dataset2)):
        assert sample1.numpy() == float(sample2.numpy())
    
    
