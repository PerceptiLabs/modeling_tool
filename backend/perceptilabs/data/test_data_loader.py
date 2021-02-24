import os
import pytest

import pandas as pd
import tensorflow as tf
import numpy as np
import pandas as pd
from skimage.io import imsave    

from perceptilabs.data.base import DataLoader, FeatureSpec


@pytest.mark.tf2x
def test_basic_structure_ok():
    data = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2','y1', 'y2']) 

    feature_specs = {
        'x1': FeatureSpec('numerical', 'input'),
        'x2': FeatureSpec('numerical', 'input'),
        'y1': FeatureSpec('numerical', 'output'),
        'y2': FeatureSpec('numerical', 'output')
    }
    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        assert inputs['x1'].numpy() == 1.0
        assert inputs['x2'].numpy() == 2.0
        assert targets['y1'].numpy() == 3.0
        assert targets['y2'].numpy() == 4.0        


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

        
@pytest.mark.tf2x
def test_image_data_is_loaded_correctly(temp_path):
    image = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    expected_image = image.astype(np.float32)
    
    image_path = os.path.join(temp_path, 'image.png')
    imsave(image_path, expected_image)
    
    data = [[image_path, 0], [image_path, 1], [image_path, 4]]
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec('image', 'input'),
        'y': FeatureSpec('numerical', 'output')
    }
    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        actual_image = inputs['x'].numpy()
        assert np.all(np.isclose(actual_image, expected_image, atol=1))


        
        
