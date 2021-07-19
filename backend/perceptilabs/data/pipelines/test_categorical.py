import os
import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import MagicMock


from perceptilabs.data.pipelines import CategoricalPipelineBuilder


def test_categorical_preprocessing_when_values_are_strings():
    values = ['cat', 'dog', 'zebra', 'zebra']
    expected = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)  
    _, _, pipeline, _ = CategoricalPipelineBuilder().build_from_dataset({}, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected


def test_categorical_preprocessing_when_values_are_string_integers():
    values = ['2', '1', '0', '0']
    expected = [
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)
    _, _, pipeline, _ = CategoricalPipelineBuilder().build_from_dataset({}, dataset)    
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected

    
    
def test_categorical_preprocessing_when_values_are_numerical():
    values = [0, 1, 2, 2]
    expected = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)
    _, _, pipeline, _ = CategoricalPipelineBuilder().build_from_dataset({}, dataset)        
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected


def test_categorical_preprocessing_when_values_are_numerical_but_unordered():
    values = [0, 2, 1, 2]
    expected = [
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)
    _, _, pipeline, _ = CategoricalPipelineBuilder().build_from_dataset({}, dataset)            
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected
    

def test_categorical_postprocessing():
    expected = ['cat', 'dog', 'car', 'car']
    
    dataset = tf.data.Dataset.from_tensor_slices(expected)
    _, _, preprocessing, postprocessing = CategoricalPipelineBuilder().build_from_dataset({}, dataset)
    processed_dataset = dataset.map(lambda x: preprocessing(x))
    
    processed_dataset = processed_dataset.map(lambda x: postprocessing(x))    

    actual = [x.numpy().decode() for x in iter(processed_dataset)]
    assert actual == expected


def test_unseen_value_has_default_preprocessed_value():
    dataset = tf.data.Dataset.from_tensor_slices(['cat', 'dog', 'zebra'])  
    _, _, pipeline, _ = CategoricalPipelineBuilder().build_from_dataset({}, dataset)                
    actual = pipeline(tf.constant('elephant')).numpy()
    expected = [0.0, 0.0, 0.0]
    assert (actual == expected).all()


def test_unseen_string_has_default_postprocessed_value():
    dataset = tf.data.Dataset.from_tensor_slices(['cat', 'dog', 'zebra'])
    _, _, _, pipeline = CategoricalPipelineBuilder().build_from_dataset({}, dataset)            

    value = pipeline([0.0, 0.0, 0.0, 1.0]).numpy()  # add an extra category
    assert value == b'<unknown>'


def test_unseen_numerical_has_default_postprocessed_value():
    dataset = tf.data.Dataset.from_tensor_slices([10, 15, 20])
    _, _, _, pipeline = CategoricalPipelineBuilder().build_from_dataset({}, dataset)                

    value = pipeline([0.0, 0.0, 0.0, 1.0]).numpy()  # add an extra category
    assert value == -1
    

def test_build_from_metadata_gives_same_results():
    dataset = tf.data.Dataset.from_tensor_slices(['cat', 'dog', 'zebra'])    

    _, _, built_preprocessing, built_postprocessing = CategoricalPipelineBuilder().build_from_dataset({}, dataset)

    
    metadata = {
        'preprocessing': built_preprocessing.metadata,
        'postprocessing': built_postprocessing.metadata
    }
    _, _, loaded_preprocessing, loaded_postprocessing = CategoricalPipelineBuilder().load_from_metadata({}, metadata)

    for x in dataset:
        y_built = built_preprocessing(x)
        y_loaded = loaded_preprocessing(x)

        assert np.all(y_built == y_loaded)
        assert np.all(built_postprocessing(y_built) == loaded_postprocessing(y_loaded))
    
    
    
