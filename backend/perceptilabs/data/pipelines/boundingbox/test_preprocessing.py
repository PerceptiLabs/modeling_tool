import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock


from perceptilabs.data.pipelines.boundingbox.preprocessing import (
    BoundingBoxPreprocessing,
)
from perceptilabs.data.settings import BoundingBoxPreprocessingSpec


def test_bounding_box_data_preprocessing():
    bounding_box_1 = ["cat", "100", "200", "50", "150"]
    bounding_box_2 = [
        "dog",
        "100",
        "200",
        "50",
        "150",
        "dog",
        "100",
        "200",
        "50",
        "150",
    ]
    bounding_boxes = [bounding_box_1] * 2 + [bounding_box_2] * 3
    preprocessing = BoundingBoxPreprocessingSpec()
    # Create the dataset
    dataset = tf.data.Dataset.from_generator(lambda: bounding_boxes, tf.string)
    # Create the pipeline
    pipeline = BoundingBoxPreprocessing.from_data(preprocessing, dataset)
    processed_dataset = dataset.map(pipeline)

    # See if the actual concrete value has the same shape as we expect

    actual = next(iter(processed_dataset))
    assert actual["categories"].numpy() == [0]
    assert actual["num_boxes"] == 1
    assert list(pipeline.metadata["mapping"].keys()) == ["cat", "dog"]
    assert actual["num_categories"] == 2
