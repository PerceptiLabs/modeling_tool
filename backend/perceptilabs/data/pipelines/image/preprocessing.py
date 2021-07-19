import numpy as np
import tensorflow as tf

from perceptilabs.data.pipelines.base import BasePipeline


class Preprocessing(BasePipeline):
    def call(self, x):
        x = tf.cast(x, dtype=tf.float32)

        if self.normalization:
            x = self.normalization(x)    
                    
        return x

    def build(self, input_shape):
        self.image_shape = input_shape
        self.normalization = self._get_normalization()

    def _get_normalization(self):
        normalization = None    
        if self.preprocessing and self.preprocessing.normalize:
            type_ = self.preprocessing.normalize_mode
            if type_ == 'standardization':
                mean = self.metadata['normalization']['pixel_mean']
                std = self.metadata['normalization']['pixel_std']                

                # Featurewise standardization: see https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator

                # TODO(anton.k): clarify if this is featurewise or samplewise in frontend.
                
                def normalization(x):
                    y = (x - mean)/(std + 0.000001)
                    return y
                
            elif type_ == 'min-max':
                min_ = self.metadata['normalization']['min_pixel_value']
                max_ = self.metadata['normalization']['max_pixel_value']                
    
                def normalization(x):
                    y = (x - min_)/(max_ - min_)
                    return y
                
        return normalization

    @classmethod
    def from_data(cls, preprocessing, dataset):
        metadata = cls.compute_metadata(preprocessing, dataset)
        return cls(
            preprocessing=preprocessing,
            metadata=metadata
        )

    @classmethod
    def compute_metadata(cls, preprocessing, dataset):

        if preprocessing and preprocessing.normalize:        
            max_pixel_value = np.iinfo(np.uint8).min
            min_pixel_value = np.iinfo(np.uint8).max
    
            sum_of_pixels = 0
            sum_of_pixel_squares = 0
            n_pixels = 0
    
            for raw_image in (tensor.numpy().astype(np.float32) for tensor in dataset):
                max_pixel_value = max(raw_image.max(), max_pixel_value)
                min_pixel_value = min(raw_image.min(), max_pixel_value)            
    
                sum_of_pixels += np.sum(raw_image)
                sum_of_pixel_squares += np.sum(np.square(raw_image))
                n_pixels += np.prod(raw_image.shape) 
    
                # Featurewise standardization: see https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator                

            pixel_mean = sum_of_pixels/n_pixels
            pixel_std = np.sqrt( sum_of_pixel_squares/n_pixels - pixel_mean**2 )
                
            metadata = {
                "image_shape": list(raw_image.shape),
                "normalization": {
                    "max_pixel_value": max_pixel_value,
                    "min_pixel_value": min_pixel_value,
                    "pixel_std": pixel_std.tolist(),
                    "pixel_mean": pixel_mean.tolist() 
                }
            }
        else:
            tensor = next(iter(dataset))
            image = tensor.numpy().astype(np.float32)
            metadata = {"image_shape": list(image.shape)}
        return metadata
