import tensorflow as tf


from perceptilabs.data.pipelines.base import PipelineBuilder


class NumericalPipelineBuilder(PipelineBuilder):
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

        normalization = None    
        if feature_spec and 'normalize' in feature_spec.preprocessing:
            type_ = feature_spec.preprocessing['normalize']['type']
            if type_ == 'standardization':
                normalization = tf.keras.layers.experimental.preprocessing.Normalization(axis=None)
                normalization.adapt(feature_dataset)
            elif type_ == 'min-max':
                max_, min_ = 0, 255
                for image in feature_dataset:
                    max_ = max(max_, tf.reduce_max(image).numpy())
                    min_ = min(min_, tf.reduce_min(image).numpy())
    
                def normalization(x):
                    y = (x - min_)/(max_ - min_)
                    return y
        
        class Pipeline(tf.keras.Model):
            def call(self, x):
                x = tf.cast(x, dtype=tf.float32)
                if normalization:
                    x = normalization(x)                
                return x
    
        return Pipeline(), None, None        
        
