import numpy as np
import tensorflow as tf
import numpy as np

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline, IdentityPipeline, DefaultAugmenter

class PreprocessingStep(BasePipeline):
    def call(self, x):
        x = tf.cast(x, dtype=tf.float32)
        if self.normalize:
            x = self.normalize(x)                
        return x

    def build(self, input_shape):
        self.normalize = self._build_normalize()
            
    def _build_normalize(self):
        if self.preprocessing and self.preprocessing.normalize:
            norm = self.preprocessing.normalize_mode

            if norm == 'standardization':
                stddev = self.metadata['stddev']
                mean = self.metadata['mean']
                return lambda x: (x - mean)/stddev
            elif norm == 'min-max':
                min_value = self.metadata['min']
                max_value = self.metadata['max']                    
                return lambda x: (x - min_value)/(max_value - min_value)

        return None


class NumericalPipelineBuilder(PipelineBuilder):
    _loader_class = None
    _augmenter_class = None
    _preprocessing_class = PreprocessingStep
    _postprocessing_class = None
    
    def _compute_processing_metadata(self, preprocessing, dataset):        
        metadata = {}
        if preprocessing and preprocessing.normalize:
            max_, min_ = 0, 2**32
            running_sum = 0
            running_squared_sum = 0

            count = 0
            for x in dataset:
                value = x.numpy()

                if value < min_:
                    min_ = value

                if value > max_:
                    max_ = value

                running_sum += value
                running_squared_sum += value**2
                count += 1

            mean = running_sum/count  # watch for overflow
            squared_mean = running_squared_sum / count  # watch for overflow
            
            metadata['mean'] = mean
            metadata['stddev'] = np.sqrt(squared_mean - mean**2)
            metadata['max'] = max_
            metadata['min'] = min_

        return metadata, {}
    
