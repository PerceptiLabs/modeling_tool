import os
import numpy as np
import tensorflow as tf
import skimage.io

from perceptilabs.data.pipelines.base import PipelineBuilder


class ImagePipelineBuilder(PipelineBuilder):
    def build(self, feature_spec=None, feature_dataset=None):
        """ Returns a keras model for preprocessing data
    
        Arguments:
            feature_spec: information about the feature (e.g., preprocessing settings)
            feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
        Returns:
            Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
            I.e., a tuple of the following format:
    
            (training_pipeline, validation_pipeline, postprocessing_pipeline)
        """
        loader = self._get_file_loader_pipeline(feature_dataset)
        loaded_dataset = feature_dataset.map(lambda x: loader(x))  # File paths -> Image tensors
        shape = self._get_image_shape(loaded_dataset)

        normalization = self._get_normalization(feature_spec, loaded_dataset)
        random_flip = self._get_random_flip(feature_spec)
    
        class Pipeline(tf.keras.Model):
            def __init__(self, is_training_pipeline):
                super().__init__()
                self.image_shape = shape
                self.is_training_pipeline = is_training_pipeline
    
            def call(self, x):
                x = loader(x)
                x = tf.cast(x, dtype=tf.float32)
    
                if normalization:
                    x = normalization(x)
    
                if self.is_training_pipeline and random_flip:
                    x = random_flip(x)
                    
                return x
    
        return Pipeline(is_training_pipeline=True), Pipeline(is_training_pipeline=False), None 
        
    def _get_random_flip(self, feature_spec):
        if feature_spec is None:
            return None

        if 'random_flip' not in feature_spec.preprocessing:
            return None

        seed = feature_spec.preprocessing['random_flip']['seed']        
        mode = feature_spec.preprocessing['random_flip']['mode'].lower()

        def random_flip(x):
            if mode in ['horizontal', 'both']:
                x = tf.image.random_flip_left_right(x, seed=seed)
            if mode in ['vertical', 'both']:
                x = tf.image.random_flip_up_down(x, seed=seed)
            return x

        return random_flip
                
    def _get_normalization(self, feature_spec, loaded_dataset):
        if feature_spec is None:
            return None

        if not feature_spec.preprocessing.get('normalize', False):
            return None

        normalization = None    
        if feature_spec and 'normalize' in feature_spec.preprocessing:
            type_ = feature_spec.preprocessing['normalize']['type']
            if type_ == 'standardization':
                normalization = tf.keras.layers.experimental.preprocessing.Normalization()
                normalization.adapt(loaded_dataset)
            elif type_ == 'min-max':
                max_, min_ = 0, 255
                for image in loaded_dataset:
                    max_ = max(max_, tf.reduce_max(image).numpy())
                    min_ = min(min_, tf.reduce_min(image).numpy())
    
                def normalization(x):
                    y = (x - min_)/(max_ - min_)
                    return y
        return normalization
        
    def _get_file_loader_pipeline(self, feature_dataset):
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
        return loader

    def _get_image_shape(self, loaded_dataset):
        return next(iter(loaded_dataset)).shape  

    
