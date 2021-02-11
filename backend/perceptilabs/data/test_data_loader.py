import pytest
import pandas as pd
import tensorflow as tf
from perceptilabs.data.base import DataLoader, FeatureSpec


@pytest.mark.tf2x
def test_ints_are_converted_to_float():
    data = [[0, 0], [1, 1], [4, 4]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec('numerical', 'input'),
        'x2': FeatureSpec('numerical', 'output')
    }
    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()


    for inputs, targets in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert targets['x2'].dtype == tf.float32        
