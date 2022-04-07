from perceptilabs.data.pipelines.image.postprocessing import MaskPostprocessing
import tensorflow as tf
import numpy as np


def test_postprocessing_returns_image():
    mask = np.random.randint(0, 9, size=(224, 224, 10))
    postprocessing = MaskPostprocessing()
    output = postprocessing(mask)
    assert output.shape == (224, 224, 1)
