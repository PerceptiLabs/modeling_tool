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


@pytest.mark.tf2x
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


@pytest.mark.tf2x
def test_output_result_has_correct_value(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')

    df = pd.DataFrame({'x1': [123, 24, 13, 45], 'y1': [1, 2, 3, 4]})
    df.to_csv(file_path, index=False)    
    
    layer_spec = OutputLayerSpec(
        feature_name='x1',
        file_path=file_path
    )

    graph_spec = MagicMock()    
    input_results = MagicMock()
    
    strategy = IoLayerStrategy()
    results = strategy.run(layer_spec, graph_spec, input_results)

    expected = {
        'output': (123,)
    }
    
    assert results.sample == expected

    
@pytest.mark.tf2x
def test_input_result_has_correct_value(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')

    df = pd.DataFrame({'x1': [123, 24, 13, 45], 'y1': [1, 2, 3, 4]})
    df.to_csv(file_path, index=False)    
    
    layer_spec = InputLayerSpec(
        feature_name='x1',
        file_path=file_path
    )

    graph_spec = MagicMock()    
    input_results = MagicMock()
    
    strategy = IoLayerStrategy()
    results = strategy.run(layer_spec, graph_spec, input_results)

    expected = {
        'output': (123,)
    }
    
    assert results.sample == expected

    
