import pytest
import numpy as np
import tensorflow as tf


from perceptilabs.data.pipelines import TextPipelineBuilder


def test_text_preprocessing():
    docs = [
        "It was the best of times",
        "it was the worst of times",
        "it was the age of wisdom",
        "it was the age of foolishness"
    ]     
    dataset = tf.data.Dataset.from_tensor_slices(docs)

    _, _, pipeline, _ = TextPipelineBuilder().build_from_dataset({}, dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    assert pipeline.num_words == 10

    output = pipeline('it wisdom wisdom wisdom age it').numpy()
    
    assert output[pipeline.word_index['wisdom']] == 3  # 2 occurrences of wisdom
    assert output[pipeline.word_index['it']] == 2  # 2 occurrences of it
    assert output[pipeline.word_index['age']] == 1  # 1 occurrences of it        
    
    
def test_build_from_metadata_gives_same_results():
    docs = [
        "It was the best of times",
        "it was the worst of times",
        "it was the age of wisdom",
        "it was the age of foolishness"
    ]     
    dataset = tf.data.Dataset.from_tensor_slices(docs)

    _, _, built_pipeline, _ = TextPipelineBuilder().build_from_dataset({}, dataset)
    
    metadata = {
        'preprocessing': built_pipeline.metadata,
    }
    _, _, loaded_pipeline, _ = TextPipelineBuilder().load_from_metadata({}, metadata)
    
    for x in dataset:
        y_built = built_pipeline(x)
        y_loaded = loaded_pipeline(x)
        assert np.all(y_built == y_loaded)
    
