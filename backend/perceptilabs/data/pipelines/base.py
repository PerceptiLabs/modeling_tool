from abc import ABC, abstractmethod


class PipelineBuilder(ABC):
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
        raise NotImplementedError


    
        
