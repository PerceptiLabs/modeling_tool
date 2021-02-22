import pickle
from unittest.mock import MagicMock
import numpy as np


from perceptilabs.trainer.stats import SampleStats


def test_get_sample_by_id():
    layer_spec = MagicMock()
    layer_spec.feature_name = 'x1'
    
    graph_spec = MagicMock()
    graph_spec.__getitem__.return_value = layer_spec

    batch = {'x1': np.array([[10, 20], [20, 30], [30, 30.0]])}
    stats = SampleStats(
        graph_spec=graph_spec,
        sample_batch=batch
    )

    expected = batch['x1'][-1]
    actual = stats.get_sample_by_layer_id(layer_spec.id_)

    assert np.all(actual == expected)


def test_get_average_ok():
    layer_spec = MagicMock()
    layer_spec.feature_name = 'x1'
    
    graph_spec = MagicMock()
    graph_spec.__getitem__.return_value = layer_spec

    batch = {'x1': np.array([[10, 20], [20, 30], [30, 30.0]])}
    stats = SampleStats(
        graph_spec=graph_spec,
        sample_batch=batch
    )

    expected = np.average(batch['x1'], axis=0)    
    actual = stats.get_batch_average(layer_spec.id_)

    assert np.all(actual == expected)

    
                        

                                                                     
                                                             
