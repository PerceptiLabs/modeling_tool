import pytest
import tensorflow as tf


from perceptilabs.data.pipelines import build_categorical_pipelines


@pytest.mark.tf2x
def test_categorical_preprocessing():
    values = ['cat', 'dog', 'car', 'car']
    expected = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)  
    pipeline, _, _ = build_categorical_pipelines(dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected

    
@pytest.mark.tf2x
def test_categorical_preprocessing_when_values_are_numerical():
    values = [1, 2, 3, 3]
    expected = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0]                        
    ]
    
    dataset = tf.data.Dataset.from_tensor_slices(values)  
    pipeline, _, _ = build_categorical_pipelines(dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))
    actual = next(iter(processed_dataset.batch(4))).numpy().tolist()
    
    assert actual == expected


@pytest.mark.tf2x
def test_categorical_postprocessing():
    expected = ['cat', 'dog', 'car', 'car']
    
    dataset = tf.data.Dataset.from_tensor_slices(expected)  
    preprocessing, _, postprocessing = build_categorical_pipelines(dataset)
    
    processed_dataset = dataset.map(lambda x: preprocessing(x))
    
    processed_dataset = processed_dataset.map(lambda x: postprocessing(x))    

    actual = [x.numpy().decode() for x in iter(processed_dataset)]
    assert actual == expected
    
