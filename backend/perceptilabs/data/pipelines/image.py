import os
import numpy as np
import tensorflow as tf
import skimage.io

def build_image_pipelines(feature_spec=None, feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data

    Arguments:
        feature_spec: information about the feature (e.g., preprocessing settings)
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
        I.e., a tuple of the following format:
    
        (training_pipeline, validation_pipeline, postprocessing_pipeline)
    """

    # NOTE: Use the dataset directly to get the shape
    # Store the shape in the Pipeline 
    image_path = next(iter(feature_dataset)).numpy().decode()
    _, ext = os.path.splitext(image_path)

    class Loader(tf.keras.Model):
        def call(self, image_path):
            if ext in ['.tiff', '.tif']:
                image_decoded = tf.py_function(self.load_tiff, [image_path], tf.uint16)
            else:
                image_encoded = tf.io.read_file(image_path)
                image_decoded = tf.io.decode_image(image_encoded)
                
            return image_decoded

        def load_tiff(self, path_tensor):
            path = path_tensor.numpy().decode()
            image = np.atleast_3d(skimage.io.imread(path).astype(np.uint16))
            image_tensor = tf.constant(image)
            return image_tensor    
        
    loader = Loader()
    loaded_dataset = feature_dataset.map(lambda x: loader(x))  # File paths -> Image tensors
    shape = next(iter(loaded_dataset)).shape  

    if feature_spec and 'normalize' in feature_spec.preprocessing:
        normalization = tf.keras.layers.experimental.preprocessing.Normalization()
        normalization.adapt(loaded_dataset)
    else:
        normalization = None
        

    class Pipeline(tf.keras.Model):
        def __init__(self):
            super().__init__()
            self.image_shape = shape

        def call(self, x):
            x = loader(x)
            x = tf.cast(x, dtype=tf.float32)

            if normalization:
                x = normalization(x)
                
            return x

    return Pipeline(), None, None
        
