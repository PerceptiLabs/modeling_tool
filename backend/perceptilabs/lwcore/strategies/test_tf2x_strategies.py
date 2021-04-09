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
from perceptilabs.data.base import FeatureSpec, DataLoader


def test_tf2x_inner_result_has_shape(script_factory_tf2x, classification_spec_basic):
    layer_spec = classification_spec_basic['layer_fc']    

    layer_helper = LayerHelper(script_factory_tf2x, layer_spec, classification_spec_basic)    
    layer_class = layer_helper.get_class()

    layer_inputs_results = MagicMock()
    layer_inputs_results.sample = {'output': np.array([1, 2, 3, 4], dtype=np.float32)}
    input_results = {'layer_inputs': layer_inputs_results}

    graph_spec = MagicMock()
    
    strategy = Tf2xInnerStrategy(script_factory_tf2x)
    results = strategy.run(layer_spec, graph_spec, input_results)

    expected = {
        'output': (3,),
        'preview': (3,),        
        'W': (4, 3),
        'b': (3,)        
    }
    
    assert results.out_shape == expected


def test_output_result_has_correct_value():
    df = pd.DataFrame({'x1': [123, 24, 13, 45], 'y1': [1, 2, 3, 4]})
    data_loader = DataLoader(
        df,
        feature_specs={
            'x1': FeatureSpec('numerical', 'input'),
            'y1': FeatureSpec('numerical', 'output')            
        }
    )
    inputs_batch, targets_batch = next(iter(data_loader.get_dataset()))
    strategy = IoLayerStrategy(targets_batch['y1'])
    
    layer_spec = OutputLayerSpec(
        feature_name='y1'
    )

    graph_spec = MagicMock()    
    input_results = MagicMock()
    
    results = strategy.run(layer_spec, graph_spec, input_results)
    expected = {
        'output': np.array([1])
    }
    assert results.sample == expected

    
def test_input_result_has_correct_value():
    df = pd.DataFrame({'x1': [123, 24, 13, 45], 'y1': [1, 2, 3, 4]})
    data_loader = DataLoader(
        df,
        feature_specs={
            'x1': FeatureSpec('numerical', 'input'),
            'y1': FeatureSpec('numerical', 'output'),            
        }
    )
    
    inputs_batch, targets_batch = next(iter(data_loader.get_dataset()))
    strategy = IoLayerStrategy(inputs_batch['x1'])
    
    layer_spec = InputLayerSpec(
        feature_name='x1'
    )
    graph_spec = MagicMock()    
    input_results = MagicMock()    

    results = strategy.run(layer_spec, graph_spec, input_results)
    expected = {
        'output': np.array([123])
    }
    assert results.sample == expected
