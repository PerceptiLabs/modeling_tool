import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock


from perceptilabs.data.pipelines.image.preprocessing import Preprocessing
from perceptilabs.data.settings import ImagePreprocessingSpec

def test_image_preprocessing():
    image = np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
    expected = image.astype(np.float32)

    # Create the dataset
    dataset = tf.data.Dataset.from_tensor_slices([image]*9)

    # Create the pipeline
    pipeline = Preprocessing.from_data(None, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()

    assert np.all(actual == expected)

    assert actual.shape == expected.shape
    assert pipeline.image_shape == expected.shape  # Verify that the pipeline records shape


def test_featurewise_standardization():
    images = [
        np.random.randint(0, 255, size=(16, 16, 3)).astype(np.uint8)
        for i in range(10)
    ]
    dataset = tf.data.Dataset.from_tensor_slices(images)
    preprocessing = ImagePreprocessingSpec(normalize=True, normalize_mode='standardization')
    pipeline = Preprocessing.from_data(preprocessing, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    processed_images = np.array([tensor.numpy() for tensor in processed_dataset])

    mean = np.mean(processed_images)
    std = np.std(processed_images)
    assert np.isclose(mean, 0.0, atol=1e-7)
    assert np.isclose(std, 1.0)


def test_normalize_minmax_norm_for_single_sample():
    max_value = 200
    min_value = 100

    images = [
        np.random.randint(min_value, max_value + 1, size=(16, 16, 3)).astype(np.uint8)
        for i in range(10)
    ]

    def normalize(x):
        y = (x - min_value)/(max_value - min_value)
        return y


    # Create the dataset
    dataset = tf.data.Dataset.from_tensor_slices(images)
    preprocessing = ImagePreprocessingSpec(normalize=True, normalize_mode='min-max')

    pipeline = Preprocessing.from_data(preprocessing, dataset)

    for original in dataset:
        expected = normalize(original.numpy()).astype(np.float32)
        actual = pipeline(original).numpy()

        assert np.all(expected == actual)
        assert actual.max() <= 1.0
        assert actual.min() >= 0.0


def test_mask_data_preprocessing():
    mask = np.random.randint(0, 11, size=(16, 16, 3)).astype(np.uint8)

    preprocessing = ImagePreprocessingSpec(mask=True)
    # Create the dataset
    dataset = tf.data.Dataset.from_tensor_slices([mask]*9)

    # Create the pipeline
    pipeline = Preprocessing.from_data(preprocessing, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    # See if the actual concrete value has the same shape as we expect
    actual = next(iter(processed_dataset)).numpy()


    assert actual.shape == (16, 16, 11)
    assert pipeline.metadata['image_shape'] == [16, 16, 11]
    assert pipeline.metadata['num_classes'] == 11


def test_mask_datatype_metadata():
    mask = np.random.randint(0, 2, size=(224, 224, 3)).astype(np.uint8)
    mask = mask*255
    preprocessing = ImagePreprocessingSpec(mask=True)
    # Create the dataset
    dataset = tf.data.Dataset.from_tensor_slices([mask]*9)

    metadata = Preprocessing.compute_metadata(preprocessing, dataset)
    assert metadata['image_shape'] == [224, 224, 2]
    assert metadata['num_classes'] == 2
    assert metadata['normalize'] == True