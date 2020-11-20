import pytest
from unittest.mock import MagicMock

import numpy as np

from perceptilabs.layers.utils import get_layer_definition
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.lwcore.strategies import Tf2xInnerStrategy


@pytest.mark.tf2x
def test_tf2x_inner_result_has_shape(script_factory_tf2x, classification_spec_basic):
    layer_spec = classification_spec_basic['layer_fc']    

    layer_helper = LayerHelper(script_factory_tf2x, layer_spec, classification_spec_basic)    
    layer_class = layer_helper.get_class()

    layer_inputs_results = MagicMock()
    layer_inputs_results.sample = {'output': np.array([1, 2, 3, 4], dtype=np.float32)}
    input_results = {'layer_inputs': layer_inputs_results}
    
    strategy = Tf2xInnerStrategy()
    results = strategy.run(layer_spec, layer_class, input_results)

    expected = {
        'output': (3,),
        'preview': (3,),        
        'W': (4, 3),
        'b': (3,)        
    }
    
    assert results.out_shape == expected

