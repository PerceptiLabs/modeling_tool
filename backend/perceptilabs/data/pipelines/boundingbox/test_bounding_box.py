import pytest
import tensorflow as tf
import numpy as np
import os
import skimage.io as sk
import tempfile
from unittest.mock import MagicMock

from perceptilabs.data.pipelines import BoundingBoxPipelineBuilder
from perceptilabs.data.settings import BoundingBoxPreprocessingSpec


def test_build_from_metadata_gives_same_results():

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
    dataset = tf.data.Dataset.from_generator(lambda: bounding_boxes, tf.string)

    preprocessing = BoundingBoxPreprocessingSpec()
    _, _, preprocessing1, _ = BoundingBoxPipelineBuilder().build_from_dataset(
        preprocessing,
        dataset,
        dataset_size=5,
        feature_name=None,
        on_status_updated=None,
    )

    metadata = {"preprocessing": preprocessing1.metadata}
    _, _, preprocessing2, _ = BoundingBoxPipelineBuilder().load_from_metadata(
        preprocessing, metadata
    )

    dataset1 = dataset.map(lambda x: preprocessing1(x))

    dataset2 = dataset.map(lambda x: preprocessing2(x))

    for sample1, sample2 in tf.data.Dataset.zip((dataset1, dataset2)):
        assert sample1["categories"] == sample2["categories"]
        assert sample1["num_boxes"] == sample2["num_boxes"]
        assert np.all(sample1["bounding_boxes"] == sample2["bounding_boxes"])
        assert sample1["num_categories"] == sample2["num_categories"]
