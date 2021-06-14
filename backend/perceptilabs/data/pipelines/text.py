import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder


class TextPipelineBuilder(PipelineBuilder):
    def build(self, feature_spec=None, feature_dataset=None):    
        """ Returns a keras model for preprocessing data of type text
    
        Arguments:
            feature_spec: information about the feature (e.g., preprocessing settings)
            feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
        Returns:
            Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
            I.e., a tuple of the following format:
        
            (training_pipeline, validation_pipeline, postprocessing_pipeline)
        """

        tokenizer = tf.keras.preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(
            (x.numpy().decode() for x in iter(feature_dataset))
        )

        class Pipeline(tf.keras.Model):
            def __init__(self):
                super().__init__()
                self._tokenizer = tokenizer
                self.word_index = tokenizer.word_index
                self.num_words = len(self.word_index)
                
            def call(self, x):
                x = tf.py_function(self.tokenize, [x], tf.float32)
                return x

            def tokenize(self, text_tensor):
                text = text_tensor.numpy().decode()
                matrix = self._tokenizer.texts_to_matrix([text], mode='count')[0]
                tensor = tf.constant(matrix, dtype=tf.float32)
                return tensor
                
    
        return Pipeline(), None, None
        

