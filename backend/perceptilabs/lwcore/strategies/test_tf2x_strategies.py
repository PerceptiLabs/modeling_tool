import pytest
from unittest.mock import MagicMock
import os

import numpy as np
import pandas as pd

from perceptilabs.layers.utils import get_layer_definition
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.lwcore.strategies import Tf2xInnerStrategy, IoLayerStrategy
from perceptilabs.layers.iooutput.spec import OutputLayerSpec
from perceptilabs.layers.ioinput.spec import InputLayerSpec
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings


def test_output_result_has_correct_value():
    df = pd.DataFrame({"x1": [123, 24, 13, 45], "y1": [1, 2, 3, 4]})
    dataset_settings = DatasetSettings(
        feature_specs={
            "x1": FeatureSpec(datatype="numerical", iotype="input"),
            "y1": FeatureSpec(datatype="numerical", iotype="target"),
        }
    )
    data_loader = DataLoader(df, dataset_settings)
    inputs_batch, targets_batch = next(iter(data_loader.get_dataset()))
    strategy = IoLayerStrategy(targets_batch["y1"])

    layer_spec = OutputLayerSpec(feature_name="y1")

    graph_spec = MagicMock()
    input_results = MagicMock()

    results = strategy.run(layer_spec, graph_spec, input_results)
    expected = {"output": np.array([1])}
    assert results.sample == expected


def test_input_result_has_correct_value():
    df = pd.DataFrame({"x1": [123, 24, 13, 45], "y1": [1, 2, 3, 4]})

    dataset_settings = DatasetSettings(
        feature_specs={
            "x1": FeatureSpec(datatype="numerical", iotype="input"),
            "y1": FeatureSpec(datatype="numerical", iotype="target"),
        }
    )
    data_loader = DataLoader(df, dataset_settings)

    inputs_batch, targets_batch = next(iter(data_loader.get_dataset()))
    strategy = IoLayerStrategy(inputs_batch["x1"])

    layer_spec = InputLayerSpec(feature_name="x1")
    graph_spec = MagicMock()
    input_results = MagicMock()

    results = strategy.run(layer_spec, graph_spec, input_results)
    expected = {"output": np.array([123])}
    assert results.sample == expected
