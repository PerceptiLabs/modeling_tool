import pytest
import numpy as np
import tensorflow as tf


from perceptilabs.data.pipelines import TextPipelineBuilder


def test_text_postprocessing():
    docs = [
        "It was the best of times",
        "it was the worst of times",
        "it was the age of wisdom",
        "it was the age of foolishness"
    ]     
    dataset = tf.data.Dataset.from_tensor_slices(docs)

    pipeline, _, _ = TextPipelineBuilder().build(feature_dataset=dataset)
    processed_dataset = dataset.map(lambda x: pipeline(x))

    assert pipeline.num_words == 10

    output = pipeline('it wisdom wisdom wisdom age it').numpy()
    
    assert output[pipeline.word_index['wisdom']] == 3  # 2 occurrences of wisdom
    assert output[pipeline.word_index['it']] == 2  # 2 occurrences of it
    assert output[pipeline.word_index['age']] == 1  # 1 occurrences of it        
    
    
