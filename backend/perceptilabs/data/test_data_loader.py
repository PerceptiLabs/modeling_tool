import os
import pytest

import skimage.io as sk
import pandas as pd
import tensorflow as tf
import numpy as np
import pandas as pd
from skimage.io import imsave
from unittest.mock import MagicMock

from perceptilabs.resources.files import FileAccess
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings, Partitions, NumericalPreprocessingSpec, ImagePreprocessingSpec


def random_image(shape, temp_path, ext):
    image = np.random.randint(0, 255, shape, dtype=np.uint8)
    idx = len(os.listdir(temp_path))
    image_path = os.path.join(temp_path, f'image{idx}{ext}')
    sk.imsave(image_path, image)
    return image_path, image


def test_basic_structure_ok():
    data = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2','y1', 'y2']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target'),
        'y2': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        assert inputs['x1'].numpy() == 1.0
        assert inputs['x2'].numpy() == 2.0
        assert targets['y1'].numpy() == 3.0
        assert targets['y2'].numpy() == 4.0        


def test_skips_unused_features():
    data = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2','y1', 'y2']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='do not use'),
        'y1': FeatureSpec(datatype='numerical', iotype='target'),
        'y2': FeatureSpec(datatype='numerical', iotype='do not use')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        assert inputs['x1'].numpy() == 1.0
        assert targets['y1'].numpy() == 3.0
        
        assert 'x2' not in inputs        
        assert 'y2' not in targets


def test_skips_columns_without_feature_spec():
    data = [[1.0, 2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0, 5.0], [1.0, 2.0, 3.0, 4.0, 5.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2','y1', 'y2', 'z1']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='do not use'),
        'y1': FeatureSpec(datatype='numerical', iotype='target'),
        'y2': FeatureSpec(datatype='numerical', iotype='do not use')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        assert inputs['x1'].numpy() == 1.0
        assert targets['y1'].numpy() == 3.0
        
        assert 'x2' not in inputs        
        assert 'y2' not in targets
        assert 'z1' not in inputs and 'z1' not in targets
        

def test_ints_are_converted_to_float():
    data = [[0, 0], [1, 1], [4, 4]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert targets['x2'].dtype == tf.float32        

        
def test_image_data_is_loaded_correctly(temp_path):
    image = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    expected_image = image.astype(np.float32)
    
    image_path = os.path.join(temp_path, 'image.png')
    imsave(image_path, expected_image)
    
    data = [[image_path, 0], [image_path, 1], [image_path, 4]]
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(datatype='image', iotype='input'),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, targets in dataset:
        actual_image = inputs['x'].numpy()
        assert np.all(np.isclose(actual_image, expected_image, atol=1))

        
def test_splitting():
    data = [[1, -1], [1, -1], [1, -1], [2, -2], [2, -2], [3, -3]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=False
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)

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


def test_splitting_rows_are_preserved():  # I.e., check that columns arent shuffled differently
    data = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0], [5.0, 5.0], [6.0, 6.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=False
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)
    
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

    
def test_splitting_rows_are_preserved_with_randomized_partitions():  # I.e., check that columns arent shuffled differently
    data = [[1.0, -1.0], [2.0, -2.0], [3.0, -3.0], [4.0, -4.0], [5.0, -5.0], [6.0, -6.0]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 


    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=True
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)
    
    def validate_set(dataset):
        for inputs, targets in dataset:
            x1, x2 = inputs['x1'].numpy(), targets['x2'].numpy()
            assert x1 == -x2
        
    validate_set(dl.get_dataset(partition='training'))
    validate_set(dl.get_dataset(partition='validation'))
    validate_set(dl.get_dataset(partition='test'))
    

def test_get_dataset_size():
    data = [[1, -1], [1, -1], [1, -1], [2, -2], [2, -2], [3, -3]]
    df = pd.DataFrame(data, columns=['x1', 'x2']) 


    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
    )

    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)

    assert dl.get_dataset_size(partition='training') == 3
    assert dl.get_dataset_size(partition='validation') == 2
    assert dl.get_dataset_size(partition='test') == 1    


def test_instantiate_binary_string_data():
    data = {'x1': ['True', 'False', 'True', 'False'], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec(datatype='binary', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32

        
def test_instantiate_binary_integer_data():
    data = {'x1': [1, 0, 1, 0], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec(datatype='binary', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32

        
def test_instantiate_binary_bool_data():
    data = {'x1': [True, False, True, False], 'y1': [1, 0, 1, 0]}
    df = pd.DataFrame(data)

    feature_specs = {
        'x1': FeatureSpec(datatype='binary', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    dataset = dl.get_dataset()

    for inputs, target in dataset:
        assert inputs['x1'].dtype == tf.float32
        assert target['y1'].dtype == tf.float32


def test_randomized_partitioning_is_random():
    n = 5
    original_x1 = np.random.random((n,)).tolist()
    original_y1 = np.random.random((n,)).tolist()

    df = pd.DataFrame.from_dict({'x1': original_x1, 'y1': original_y1})
    
    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target')
    }

    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=True,
        seed=1234
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)

    actual_x1 = []
    actual_y1 = []

    # Get all samples, make sure that the order is different.
    for inputs, targets in dl.get_dataset(partition='training'):
        actual_x1.append(inputs['x1'].numpy())
        actual_y1.append(targets['y1'].numpy())
        
    for inputs, targets in dl.get_dataset(partition='validation'):
        actual_x1.append(inputs['x1'].numpy())
        actual_y1.append(targets['y1'].numpy())
        
    for inputs, targets in dl.get_dataset(partition='test'):
        actual_x1.append(inputs['x1'].numpy())
        actual_y1.append(targets['y1'].numpy())
        
    assert not np.all(np.isclose(original_x1, actual_x1))
    assert not np.all(np.isclose(original_y1, actual_y1))    


def test_randomized_partitioning_with_same_seed_are_equal():
    n = 5
    x = np.random.random((n,)).tolist()
    y = np.random.random((n,)).tolist()

    df = pd.DataFrame.from_dict({'x': x, 'y': y})
    
    feature_specs = {
        'x': FeatureSpec(datatype='numerical', iotype='input'),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    partitions = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=True,
        seed=1234
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl1 = DataLoader(df, dataset_settings)
    dl2 = DataLoader(df, dataset_settings)    
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.isclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.isclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )


def test_randomized_partitioning_with_diff_seed_are_unequal():
    n = 5
    x = np.random.random((n,)).tolist()
    y = np.random.random((n,)).tolist()

    df = pd.DataFrame.from_dict({'x': x, 'y': y})
    
    feature_specs = {
        'x': FeatureSpec(datatype='numerical', iotype='input'),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    partitions1 = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=True,
        seed=1234
    )
    dataset_settings1 = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions1
    )
    dl1 = DataLoader(df, dataset_settings1)

    partitions2 = Partitions(
        training_ratio=3/6,
        validation_ratio=2/6,
        test_ratio=1/6,        
        randomized=True,
        seed=100
    )
    dataset_settings2 = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions2
    )
    dl2 = DataLoader(df, dataset_settings2)

    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.isclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.isclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert not datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert not datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert not datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )


def test_shuffle_gives_random_data():
    n = 5
    original_x1 = np.random.random((n,)).tolist()
    original_y1 = np.random.random((n,)).tolist()

    df = pd.DataFrame.from_dict({'x1': original_x1, 'y1': original_y1})
    
    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'y1': FeatureSpec(datatype='numerical', iotype='target')
    }

    partitions = Partitions(
        randomized=True,
        seed=1234
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)
    
    def dataset_to_list(dataset):
        data_list = []
        for inputs, outputs in dataset:
            xy = (inputs['x1'].numpy(), outputs['y1'].numpy())
            data_list.append(xy)
        return data_list
    
    data_unshuffled_1 = dataset_to_list(dl.get_dataset(shuffle=False))
    data_unshuffled_2 = dataset_to_list(dl.get_dataset(shuffle=False))    
    data_shuffled_1 = dataset_to_list(dl.get_dataset(shuffle=True, shuffle_seed=123))
    data_shuffled_2 = dataset_to_list(dl.get_dataset(shuffle=True, shuffle_seed=456))

    assert data_unshuffled_1 == data_unshuffled_2
    assert data_unshuffled_1 != data_shuffled_1
    assert data_unshuffled_1 != data_shuffled_2
    assert data_shuffled_1 != data_shuffled_2            


def test_image_data_is_augmented_consistently(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((32, 32, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl1 = DataLoader(df, dataset_settings)
    dl2 = DataLoader(df, dataset_settings)    
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )


def test_image_data_with_diff_seed_is_not_augmented_consistently(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((32, 32, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    fs1 = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    ds1 = DatasetSettings(feature_specs=fs1)

    fs2 = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=False,
                random_flip_mode='horizontal',
                random_flip_seed=100
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    ds2 = DatasetSettings(feature_specs=fs2)
    
    dl1 = DataLoader(df, ds1)
    dl2 = DataLoader(df, ds2)    

    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert not datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert not datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert not datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )

    
def test_image_data_is_augmented_consistently_for_repeated_calls(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((32, 32, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl = DataLoader(df, dataset_settings)
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert datasets_are_equal(
        dl.get_dataset(),
        dl.get_dataset()
    )


def test_image_data_is_augmented_consistently_for_repeated_calls_with_shuffle(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((8, 8, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, idx] for idx, img in enumerate(image_paths)]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl = DataLoader(df, dataset_settings)
    
    def datasets_are_equivalent(set1, set2):  # I.e., order doesn't matter
        dataset1 = {y['y'].numpy(): x['x'].numpy() for x, y in set1}
        dataset2 = {y['y'].numpy(): x['x'].numpy() for x, y in set2}

        if len(dataset1) != len(dataset2):
            return False

        for idx in dataset1.keys():  # Assumes the labels are unique
            if not np.allclose(dataset1[idx], dataset2[idx]):
                return False
        return True
        

    assert datasets_are_equivalent(
        dl.get_dataset(shuffle=True, shuffle_seed=123),
        dl.get_dataset(shuffle=True, shuffle_seed=456)
    )


def test_image_data_is_augmented_consistently_with_flip_and_crop(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((16, 16, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='both',
                random_flip_seed=123,
                random_crop=True,
                random_crop_seed=200,
                random_crop_height=8,
                random_crop_width=12,
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl1 = DataLoader(df, dataset_settings)
    dl2 = DataLoader(df, dataset_settings)    
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    for inputs, targets in dl1.get_dataset():
        assert inputs['x'].shape == (8, 12, 3)

    assert datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )
    

def test_image_data_is_augmented_consistently_with_flip_crop_and_rotate(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((16, 16, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='both',
                random_flip_seed=123,
                random_crop=True,
                random_crop_seed=200,
                random_crop_height=8,
                random_crop_width=12,
                random_rotation=True,
                random_rotation_seed=20,
                random_rotation_factor=0.3,
                random_rotation_fill_value=10,
                random_rotation_fill_mode='constant'
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl1 = DataLoader(df, dataset_settings)
    dl2 = DataLoader(df, dataset_settings)    
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    for inputs, targets in dl1.get_dataset():
        assert inputs['x'].shape == (8, 12, 3)

    assert datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )


@pytest.mark.parametrize("ext", ['.png', '.tiff'])    
def test_image_data_resize_has_correct_shape(temp_path, ext):
    image_paths = []
    for _ in range(3):
        path, data = random_image((16, 16, 3), temp_path, ext)
        image_paths.append(path)

    for _ in range(3):
        path, data = random_image((24, 32, 3), temp_path, ext)
        image_paths.append(path)

        
    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                resize=True,
                resize_mode='custom',
                resize_height=32,
                resize_width=8
                
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl = DataLoader(df, dataset_settings)

    for inputs, targets in dl.get_dataset():
        assert inputs['x'].shape == (32, 8, 3)


def test_image_data_resize_has_correct_shape_mixed_extensions(temp_path):
    image_paths = []
    for _ in range(3):
        path, data = random_image((16, 16, 3), temp_path, '.png')
        image_paths.append(path)

    for _ in range(3):
        path, data = random_image((24, 32, 3), temp_path, '.tiff')
        image_paths.append(path)

        
    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                resize=True,
                resize_mode='custom',
                resize_height=32,
                resize_width=8
                
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl = DataLoader(df, dataset_settings)

    for inputs, targets in dl.get_dataset():
        assert inputs['x'].shape == (32, 8, 3)
        

def test_repeated_dataset_ok():
    df = pd.DataFrame.from_dict(
        {
            'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'y': [-1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
        }
    )

    feature_specs = {
        'x': FeatureSpec(datatype='numerical', iotype='input'),
        'y': FeatureSpec(datatype='numerical', iotype='target'),
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings, num_repeats=2)


    def dataset_to_lists(dataset):
        i = []
        x = []
        y = []

        for index, inputs, targets in dataset:
            i.append(index.numpy())
            x.append(inputs['x'].numpy())
            y.append(targets['y'].numpy())

        return i, x, y

    i, x, y = dataset_to_lists(dl.get_dataset(partition='training', drop_index=False))
    assert i == [0, 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16]
    assert x == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    assert y == [-1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0]

    i, x, y = dataset_to_lists(dl.get_dataset(partition='validation', drop_index=False))
    assert i == [7, 8]
    assert x == [8.0, 9.0]
    assert y == [-8.0, -9.0]

    i, x, y = dataset_to_lists(dl.get_dataset(partition='test', drop_index=False))
    assert i == [9]    
    assert x == [10.0]
    assert y == [-10.0]


def test_compute_metadata_is_identical(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((32, 32, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl1 = DataLoader(df, dataset_settings)
    metadata = DataLoader.compute_metadata(df, dataset_settings)

    assert metadata == dl1.metadata
    

def test_loading_with_metadata_gives_same_data(temp_path):
    image_paths = []
    for _ in range(20):
        path, data = random_image((32, 32, 3), temp_path, '.png')
        image_paths.append(path)

    data = [[img, 0] for img in image_paths]  # Image, label
    df = pd.DataFrame(data, columns=['x', 'y']) 

    feature_specs = {
        'x': FeatureSpec(
            datatype='image',
            iotype='input',
            preprocessing=ImagePreprocessingSpec(
                random_flip=True,
                random_flip_mode='horizontal',
                random_flip_seed=123
            )
        ),
        'y': FeatureSpec(datatype='numerical', iotype='target')
    }
    dataset_settings = DatasetSettings(feature_specs=feature_specs)

    dl1 = DataLoader(df, dataset_settings)
    dl2 = DataLoader(df, dataset_settings, metadata=dl1.metadata)    
    
    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.allclose(x1['x'].numpy(), x2['x'].numpy()) and 
                np.allclose(y1['y'].numpy(), y2['y'].numpy())
            )
            if not equal:
                return False
        return True

    assert datasets_are_equal(
        dl1.get_dataset(partition='training'),
        dl2.get_dataset(partition='training')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='validation'),
        dl2.get_dataset(partition='validation')
    )
    assert datasets_are_equal(
        dl1.get_dataset(partition='test'),
        dl2.get_dataset(partition='test')
    )
    

@pytest.mark.parametrize("random_partitions", [False, True])
def test_get_dataframe_equals_original(random_partitions):
    n_rows = 60
    ratios = {'training': 3/6, 'validation': 2/6, 'test': 1/6}
    
    data = {
        'x1': [x for x in range(n_rows)],
        'x2': [x**2 for x in range(n_rows)]
    }
    df = pd.DataFrame(data) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=ratios['training'],
        validation_ratio=ratios['validation'],
        test_ratio=ratios['test'],
        randomized=random_partitions
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings)

    assert dl.get_data_frame().equals(df)
    assert dl.get_data_frame(partition='original').equals(df)
    assert len(dl.get_data_frame(partition='all')) == n_rows

    for partition, ratio in ratios.items():
        partition_df = dl.get_data_frame(partition=partition)
        assert len(partition_df) == ratio*n_rows
    
    
@pytest.mark.parametrize("random_partitions", [False, True])
def test_get_dataframe_partition_matches_loader_partition(random_partitions):
    n_rows = 60
    ratios = {'training': 3/6, 'validation': 2/6, 'test': 1/6}
    
    data = {
        'x1': [x for x in range(n_rows)],
        'x2': [x**2 for x in range(n_rows)]
    }
    df = pd.DataFrame(data) 

    feature_specs = {
        'x1': FeatureSpec(datatype='numerical', iotype='input'),
        'x2': FeatureSpec(datatype='numerical', iotype='target'),
    }
    partitions = Partitions(
        training_ratio=ratios['training'],
        validation_ratio=ratios['validation'],
        test_ratio=ratios['test'],
        randomized=random_partitions
    )
    dataset_settings = DatasetSettings(
        feature_specs=feature_specs,
        partitions=partitions
    )
    dl = DataLoader(df, dataset_settings).ensure_initialized()

    def datasets_are_equal(set1, set2):
        for (x1, y1), (x2, y2) in zip(set1, set2):
            equal = (
                np.isclose(x1['x1'].numpy(), x2['x1'].numpy()) and 
                np.isclose(y1['x2'].numpy(), y2['x2'].numpy())
            )
            if not equal:
                return False
        return True

    for partition in list(ratios.keys()) + ['all']:
        # Create a new loader based on training/validation/test dataframe ONLY.
        # its content should be an exact copy of the original training/validation/test datasets
        
        partition_settings = DatasetSettings(
            feature_specs=feature_specs,
            partitions=Partitions(randomized=False)
        )                
        partition_df = dl.get_data_frame(partition=partition)
        partition_dl = DataLoader(partition_df, partition_settings)
        assert datasets_are_equal(
            partition_dl.get_dataset(partition='all', shuffle=False),
            dl.get_dataset(partition=partition, shuffle=False)
        )

    
