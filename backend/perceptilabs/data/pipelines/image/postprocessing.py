import tensorflow as tf
import numpy as np
from perceptilabs.data.pipelines.base import BasePipeline
import matplotlib.pyplot as plt

class MaskPostprocessing(BasePipeline):        
    def call(self, x):
        num_categories = x.shape[-1]
        x = tf.argmax(x, axis=-1) # Convert from one-hot encoded values
        x = tf.expand_dims(x, axis=-1)
        x = x/(num_categories-1)
        return x
