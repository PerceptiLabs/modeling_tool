import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline


class PreprocessingStep(BasePipeline):
    def call(self, x):
        if x.dtype in [tf.int32, tf.bool]:
            return self.lookup_number(x)
        elif x.dtype == tf.string:
            return self.lookup_string(x)
        else:
            raise ValueError("Invalid Binary inputs")                

    def build(self, tensor_shape):
        self.lookup_string = self._build_string_lookup()
        self.lookup_number = self._build_number_lookup()

    def _build_number_lookup(self):
        return lambda x: tf.cast(x, tf.float32)
        
    def _build_string_lookup(self):
        positives = ['true', 'spam']
        negatives = ['false', 'ham']
        
        keys = tf.constant(positives + negatives)
        values = tf.constant([1.0 for _ in range(len(positives))] + [0.0 for _ in range(len(negatives))])
            
        init = tf.lookup.KeyValueTensorInitializer(keys, values)
        self.table = tf.lookup.StaticHashTable(init, default_value=0)
                                 
        def func(x):
            x = tf.strings.lower(x)
            x = self.table.lookup(x)
            return x                

        return func    


class BinaryPipelineBuilder(PipelineBuilder):
    _loader_class = None
    _augmenter_class = None
    _preprocessing_class = PreprocessingStep
    _postprocessing_class = None

    def _compute_processing_metadata(self, preprocessing, dataset):
        return {'n_categories': 1}, {}
    
