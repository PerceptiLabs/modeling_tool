import pytest
import os
from unittest.mock import MagicMock
import tensorflow as tf


from perceptilabs.data.pipelines import BinaryPipelineBuilder


def test_binary_preprocessing_ints():
    dataset = tf.data.Dataset.from_tensor_slices([1, 0])
    _, _, pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)

    assert pipeline(1) == 1.0
    assert pipeline(0) == 0.0    


def test_binary_preprocessing_bool():
    dataset = tf.data.Dataset.from_tensor_slices([True, False])
    _, _, pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)    

    assert pipeline(tf.constant(True)) == 1.0
    assert pipeline(tf.constant(False)) == 0.0    
    

def test_binary_preprocessing_strings():
    dataset = tf.data.Dataset.from_tensor_slices(['true', 'True'])
    _, _, pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)    

    assert pipeline(tf.constant('true')) == 1.0
    assert pipeline(tf.constant('false')) == 0.0    
    assert pipeline(tf.constant('True')) == 1.0
    assert pipeline(tf.constant('False')) == 0.0    
    assert pipeline(tf.constant('TRUE')) == 1.0
    assert pipeline(tf.constant('FALSE')) == 0.0    


def test_binary_preprocessing_spam_ham():
    dataset = tf.data.Dataset.from_tensor_slices(['Ham', 'spam'])
    _, _, pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)    
    
    assert pipeline(tf.constant('spam')) == 1.0
    assert pipeline(tf.constant('ham')) == 0.0    
    assert pipeline(tf.constant('Spam')) == 1.0
    assert pipeline(tf.constant('Ham')) == 0.0    
    assert pipeline(tf.constant('SPAM')) == 1.0
    assert pipeline(tf.constant('HAM')) == 0.0    

    
def test_binary_preprocessing_num_categories():
    dataset = tf.data.Dataset.from_tensor_slices(['Ham', 'spam'])
    _, _, pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)    
    pipeline.metadata['n_categories'] == 1


def test_build_from_metadata_gives_same_results():
    dataset = tf.data.Dataset.from_tensor_slices(['Ham', 'spam'])
    _, _, built_pipeline, _ = BinaryPipelineBuilder().build_from_dataset({}, dataset)    

    metadata = {'preprocessing': built_pipeline.metadata}
    _, _, loaded_pipeline, _ = BinaryPipelineBuilder().load_from_metadata({}, metadata)
    
    dataset1 = dataset.map(lambda x: built_pipeline(x))
    dataset2 = dataset.map(lambda x: loaded_pipeline(x))        

    for sample1, sample2 in tf.data.Dataset.zip((dataset1, dataset2)):
        assert sample1.numpy() == float(sample2.numpy())
    
    
    
