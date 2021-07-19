import numpy as np
import tensorflow as tf
import skimage.io
import tensorflow_addons as tfa

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline



class Augmenter(BasePipeline):
    def call(self, x):
        index, image = x

        if self.random_crop:
            image = self.random_crop(image, index)            

        if self.random_flip:
            image = self.random_flip(image, index)
            
        if self.random_rotation:
            image = self.random_rotation(image, index)
        
        return image

    def build(self, input_shape):
        _, original_shape = input_shape  # Drop index
        self.random_flip = self._get_random_flip()    
        self.random_rotation = self._get_random_rotation()        
        self.random_crop = self._get_random_crop(original_shape)

    def _get_random_flip(self):
        if not self.preprocessing or not self.preprocessing.random_flip:
            return None

        seed = self.preprocessing.random_flip_seed
        mode = self.preprocessing.random_flip_mode.lower()

        def random_flip(x, index):
            if mode in ['horizontal', 'both']:
                x = tf.image.stateless_random_flip_left_right(x, seed=(index, seed))
            if mode in ['vertical', 'both']:
                x = tf.image.stateless_random_flip_up_down(x, seed=(index, seed))
            return x
        
        return random_flip
    
    def _get_random_rotation(self):
        if not self.preprocessing or not self.preprocessing.random_rotation:
            return None        

        seed = self.preprocessing.random_rotation_seed
        factor = self.preprocessing.random_rotation_factor
        fill_mode = self.preprocessing.random_rotation_fill_mode
        fill_value = self.preprocessing.random_rotation_fill_value or 0
        interpolation = self.preprocessing.random_rotation_interpolation or 'bilinear'

        def random_rotation(x, index):
            scalar_angle = factor * tf.random.stateless_uniform(shape=(1,), seed=(seed, index))
            x = tfa.image.rotate(
                x, angles=scalar_angle, interpolation=interpolation,
                fill_mode=fill_mode, fill_value=fill_value
            )                
            return x
        
        return random_rotation
        
    def _get_random_crop(self, original_shape):
        if not self.preprocessing or not self.preprocessing.random_crop:
            return None
        
        seed = self.preprocessing.random_crop_seed
        height = self.preprocessing.random_crop_height
        width = self.preprocessing.random_crop_width
        original_height, original_width, n_channels = original_shape

        if n_channels is None:
            n_channels = self.metadata['n_channels']

        if original_height and height > original_height:
            raise ValueError(f"Error in random cropping: Target height ({height}) cannot be greater than original height ({original_height})!")
        if original_width and width > original_width:
            raise ValueError(f"Error in random cropping: Target width ({width}) cannot be greater than original width ({original_width})!")        

        def random_crop(x, index):
            y = tf.image.stateless_random_crop(
                value=x,
                size=(height, width, n_channels),
                seed=(seed, index)
            )
            return y
        
        return random_crop

    @classmethod
    def compute_metadata(cls, dataset, preprocessing):
        index, image = next(iter(dataset))
        _, _, n_channels = image.shape        
        metadata = {
            "n_channels": n_channels
        }
        return metadata        
