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

        
@pytest.mark.tf2x
def test_splitting():
    data = [[1, -1], [1, -1], [1, -1], [2, -2], [2, -2], [3, -3]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec('numerical', 'input'),
        'x2': FeatureSpec('numerical', 'output'),
    }
    dl = DataLoader(
        df, feature_specs, partitions={'training': 3/6, 'validation': 2/6, 'test': 1/6}
    )
    
    def validate_set(dataset, expected_size, expected_x1, expected_x2):
        assert len(list(dataset)) == expected_size
        for inputs, targets in dataset:
            assert inputs['x1'].numpy() == expected_x1
            assert targets['x2'].numpy() == expected_x2
            
    validate_set(
        dl.get_dataset(partition='training'),
        expected_size=3,
        expected_x1=1.0,
        expected_x2=-1.0
    )
    validate_set(
        dl.get_dataset(partition='validation'),
        expected_size=2,
        expected_x1=2.0,
        expected_x2=-2.0
    )
    validate_set(
        dl.get_dataset(partition='test'),
        expected_size=1,
        expected_x1=3.0,
        expected_x2=-3.0
    )


@pytest.mark.tf2x
def test_splitting_rows_are_preserved():  # I.e., check that columns arent shuffled differently
    data = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0], [5.0, 5.0], [6.0, 6.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec('numerical', 'input'),
        'x2': FeatureSpec('numerical', 'output'),
    }
    dl = DataLoader(
        df, feature_specs, partitions={'training': 3/6, 'validation': 2/6, 'test': 1/6}
    )
    
    def validate_set(dataset, expected_rows):
        for inputs, targets in dataset:
            actual_row = [inputs['x1'].numpy(), targets['x2'].numpy()]
            assert actual_row in expected_rows
        
    validate_set(
        dl.get_dataset(partition='training'),
        expected_rows=[[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]
    )
    validate_set(
        dl.get_dataset(partition='validation'),
        expected_rows=[[4.0, 4.0], [5.0, 5.0]]
    )
    validate_set(
        dl.get_dataset(partition='test'),
        expected_rows=[[6.0, 6.0]] 
    )
    

@pytest.mark.tf2x
def test_get_dataset_size():
    data = [[1, -1], [1, -1], [1, -1], [2, -2], [2, -2], [3, -3]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec('numerical', 'input'),
        'x2': FeatureSpec('numerical', 'output'),
    }
    dl = DataLoader(
        df, feature_specs, partitions={'training': 3/6, 'validation': 2/6, 'test': 1/6}
    )

    assert dl.get_dataset_size(partition='training') == 3
    assert dl.get_dataset_size(partition='validation') == 2
    assert dl.get_dataset_size(partition='test') == 1    


@pytest.mark.tf2x
def test_instantiate_binary_string_data():
    data = {'x1': ['True', 'False', 'True', 'False'], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec('binary', 'input'),
        'y1': FeatureSpec('numerical', 'output')
    }

    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32

@pytest.mark.tf2x
def test_instantiate_binary_integer_data():
    data = {'x1': [1, 0, 1, 0], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec('binary', 'input'),
        'y1': FeatureSpec('numerical', 'output')
    }

    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32

@pytest.mark.tf2x
def test_instantiate_binary_bool_data():
    data = {'x1': [True, False, True, False], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec('binary', 'input'),
        'y1': FeatureSpec('numerical', 'output')
    }

    dl = DataLoader(df, feature_specs)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32