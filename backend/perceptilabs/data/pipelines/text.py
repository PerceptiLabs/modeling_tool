import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline


class PreprocessingStep(BasePipeline):
    def build(self, input_shape):
        self._tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
            self.metadata['tokenizer']
        )
        self.word_index = self._tokenizer.word_index
        self.num_words = len(self.word_index)
                
    def call(self, x):
        x = tf.py_function(self.tokenize, [x], tf.float32)
        return x
        
    def tokenize(self, text_tensor):
        text = text_tensor.numpy().decode()
        matrix = self._tokenizer.texts_to_matrix([text], mode='count')[0]
        tensor = tf.constant(matrix, dtype=tf.float32)
        return tensor
    

class TextPipelineBuilder(PipelineBuilder):
    _loader_class = None
    _augmenter_class = None
    _preprocessing_class = PreprocessingStep
    _postprocessing_class = None
    
    def _compute_processing_metadata(self, preprocessing, dataset):
        tokenizer = tf.keras.preprocessing.text.Tokenizer()
        tokenizer.fit_on_texts(
            (x.numpy().decode() for x in iter(dataset))
        )
        metadata = {'tokenizer': tokenizer.to_json()}        
        return metadata, {}
        
