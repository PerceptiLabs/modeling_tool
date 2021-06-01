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
        if feature_spec and feature_spec.preprocessing.get('normalize', False) and feature_dataset:
            normalization = tf.keras.layers.experimental.preprocessing.Normalization(axis=None)
            normalization.adapt(feature_dataset)
        else:
            normalization = None
        
        class Pipeline(tf.keras.Model):
            def call(self, x):
                x = tf.cast(x, dtype=tf.float32)
                if normalization:
                    x = normalization(x)                
                return x
    
        return Pipeline(), None, None        
        
