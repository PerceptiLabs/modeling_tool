import os
import collections
import numpy as np
import tensorflow as tf
import skimage.io
import tensorflow_addons as tfa

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
        shape_info = self._get_shape_info(loaded_dataset)

        shape_transformations = self._get_shape_transformations(feature_spec, shape_info)
        reshaped_dataset, final_shape = self._apply_shape_transformations(shape_transformations, shape_info['mode'], loaded_dataset)  # Things like normalization should be based on the new shape
        
        random_flip = self._get_random_flip(feature_spec)
        random_rotation = self._get_random_rotation(feature_spec)        
        normalization = self._get_normalization(feature_spec, reshaped_dataset)
    
        class Pipeline(tf.keras.Model):
            def __init__(self, is_training_pipeline):
                super().__init__()
                self.image_shape = final_shape
                self.is_training_pipeline = is_training_pipeline
    
            def call(self, x):
                x = loader(x)
                x = tf.cast(x, dtype=tf.float32)

                if shape_transformations:
                    x = shape_transformations(x)                
                
                if self.is_training_pipeline and random_flip:
                    x = random_flip(x)

                if self.is_training_pipeline and random_rotation:
                    x = random_rotation(x)
                    
                if normalization:
                    x = normalization(x)    
                    
                return x
    
        return Pipeline(is_training_pipeline=True), Pipeline(is_training_pipeline=False), None


    def _apply_shape_transformations(self, shape_transformations, original_shape, loaded_dataset):
        if shape_transformations:
            reshaped_dataset = loaded_dataset.map(lambda x: shape_transformations(x))
            final_shape = next(iter(reshaped_dataset)).shape
        else:
            reshaped_dataset = loaded_dataset            
            final_shape = original_shape

        return reshaped_dataset, final_shape


    def _get_shape_transformations(self, feature_spec, shape_info):
        resize, resize_shape = self._get_resize(feature_spec, shape_info)        
        random_crop = self._get_random_crop(feature_spec, resize_shape)

        def shape_transformations(x): 
            if resize:
                x = resize(x)
            if random_crop:
                x = random_crop(x)
            return x

        return shape_transformations

    def _get_resize(self, feature_spec, shape_info):
        if feature_spec is None:
            return None, shape_info['mode']
        
        if 'resize' not in feature_spec.preprocessing:
            return None, shape_info['mode']

        mode = feature_spec.preprocessing['resize']['mode']
        if mode == 'automatic':
            automatic_type = feature_spec.preprocessing['resize']['type']
            height, width, _ = shape_info[automatic_type]
        elif mode == 'custom':
            height = feature_spec.preprocessing['resize']['height']
            width = feature_spec.preprocessing['resize']['width']

            if height == 0:
                raise ValueError("Target height cannot be 0")
            if width == 0:
                raise ValueError("Target width cannot be 0")
            
        else:
            raise ValueError(f"Unknown resize mode {mode}")
            
        _, _, n_channels = shape_info['mode']  # Assume number of channels are uniform
        
        def resize(x):
            return tf.image.resize(x, (height, width))

        return resize, (height, width, n_channels)

    def _get_random_crop(self, feature_spec, original_shape):
        if feature_spec is None:
            return None
        
        if 'random_crop' not in feature_spec.preprocessing:
            return None

        seed = feature_spec.preprocessing['random_crop']['seed']        
        height = feature_spec.preprocessing['random_crop']['height']
        width = feature_spec.preprocessing['random_crop']['width']
        original_height, original_width, n_channels = original_shape
        
        if height > original_height:
            raise ValueError(f"Error in random cropping: Target height ({height}) cannot be greater than original height ({original_height})!")
        if width > original_width:
            raise ValueError(f"Error in random cropping: Target width ({width}) cannot be greater than original width ({original_width})!")        

        def random_crop(x):
            y = tf.image.random_crop(value=x, size=(height, width, n_channels), seed=seed)
            return y
        
        return random_crop

    def _get_random_rotation(self, feature_spec):
        if feature_spec is None:
            return None

        if 'random_rotation' not in feature_spec.preprocessing:
            return None
        

        seed = feature_spec.preprocessing['random_rotation']['seed']
        factor = feature_spec.preprocessing['random_rotation']['factor']        
        fill_mode = feature_spec.preprocessing['random_rotation']['fill_mode']
        fill_value = feature_spec.preprocessing['random_rotation'].get('fill_value', 0.0)      
        interpolation = 'bilinear'

        number_generator = tf.random.Generator.from_seed(seed)

        def random_rotation(x):
            scalar_angle = factor * number_generator.normal([])
            x = tfa.image.rotate(
                x, angles=scalar_angle, interpolation=interpolation,
                fill_mode=fill_mode, fill_value=fill_value
            )                
            return x
        
        return random_rotation
        
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
        _, ext = os.path.splitext(image_path.lower())

        class Loader(tf.keras.Model):
            def call(self, image_path):
                if ext in ['.tiff', '.tif']:
                    image_decoded = tf.py_function(self.load_tiff, [image_path], tf.uint16)
                    image_decoded.set_shape([None, None, None])  # Make sure the shape is present
                elif ext in ['.jpg', '.jpeg', '.png']:
                    image_encoded = tf.io.read_file(image_path)
                    image_decoded = tf.image.decode_image(image_encoded, expand_animations=False)  # animated images give no shape: https://stackoverflow.com/questions/44942729/tensorflowvalueerror-images-contains-no-shape
                else:
                    raise NotImplementedError(f"Cannot decode files of type {ext}")

                image_decoded = image_decoded[:, :, :3]  # DISCARD ALPHA CHANNEL                    
                return image_decoded
    
            def load_tiff(self, path_tensor):
                path = path_tensor.numpy().decode()
                image = np.atleast_3d(skimage.io.imread(path).astype(np.uint16))
                image_tensor = tf.constant(image)
                return image_tensor

        loader = Loader()
        return loader

    def _get_shape_info(self, loaded_dataset):
        channels = None
        max_height = -1
        max_width = -1
        min_height = 10**10
        min_width = 10**10
        running_height = 0
        running_width = 0
        frequencies = collections.defaultdict(int)

        count = 0
        for image in loaded_dataset:
            height, width, channels = shape = tuple(image.shape)
            frequencies[shape] += 1

            max_height = max(max_height, height)
            max_width = max(max_width, width)            
            min_height = min(min_height, height)
            min_width = min(min_width, width)

            running_height += height
            running_width += width
            count += 1

        max_shape = (max_height, max_width, channels)
        min_shape = (min_height, min_width, channels)        

        mean_height = int(running_height/count)
        mean_width = int(running_width/count)
        mean_shape = (mean_height, mean_width, channels)

        mode_shape, mode_count = None, -1
        for shape, count in frequencies.items():
            if count > mode_count:
                mode_shape = shape
                mode_count = count

        shape_info = {
            'mode': mode_shape,
            'mean': mean_shape,
            'max': max_shape,
            'min': min_shape,
            'is_uniform': (mode_shape == mean_shape == max_shape == min_shape)
        }
        return shape_info

