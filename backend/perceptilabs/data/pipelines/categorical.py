import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder, BasePipeline

PRECISION = 2
class PreprocessingStep(BasePipeline):
    def build(self, tensor_shape):
        categories_tensor = tf.constant(list(self.metadata['mapping'].keys()))
        indices_tensor = tf.constant(list(self.metadata['mapping'].values()))
        init = tf.lookup.KeyValueTensorInitializer(categories_tensor, indices_tensor)
        self._lookup_table = tf.lookup.StaticHashTable(init, default_value=-1)

    def call(self, x):
        if self.metadata['dtype'] == float:
            x = tf.strings.as_string(x, precision=PRECISION)
        x = self._lookup_table.lookup(x)
        x = tf.one_hot(x, self.n_categories)
        return x

    @property
    def n_categories(self):
        return len(self.metadata['mapping'])


class PostprocessingStep(BasePipeline):
    def build(self, tensor_shape):
        categories_tensor = tf.constant(list(self.metadata['mapping'].keys()))
        indices_tensor = tf.constant(list(self.metadata['mapping'].values()))

        init = tf.lookup.KeyValueTensorInitializer(indices_tensor, categories_tensor)
        self._lookup_table = tf.lookup.StaticHashTable(
            init,
            default_value=('<unknown>' if categories_tensor.dtype is tf.string else -1)
        )

    def call(self, x):
        x = tf.argmax(x, axis=-1) # Convert from one-hot encoded values
        x = tf.cast(x, tf.int32)
        x = self._lookup_table.lookup(x)
        if self.metadata['dtype'] == float:
            x = tf.strings.to_number(x)
        return x

    @property
    def n_categories(self):
        return len(self.metadata['mapping'])


class CategoricalPipelineBuilder(PipelineBuilder):
    _loader_class = None
    _augmenter_class = None
    _preprocessing_class = PreprocessingStep
    _postprocessing_class = PostprocessingStep

    def _compute_processing_metadata(self, preprocessing, dataset, on_status_updated=None):
        """ Loops over the dataset and maps values to an index (e.g., cat -> 0) """
        dtypes = set()
        unique_values = set()
        size = len(dataset)
        for index, tensor in enumerate(dataset):
            value = tensor.numpy()

            if isinstance(value, bytes):
                value = value.decode()
            else:
                value = value.item() # Convert to native python type
                
            if isinstance(value, float):
                dtype = type(value)
                value = "%.*f"%(PRECISION, value)
            else:
                dtype = type(value)

            unique_values.add(value)
            dtypes.add(dtype)

            if on_status_updated:
                on_status_updated(index=index, size=size)

        if len(dtypes) > 1:
            raise RuntimeError(f"Dataset has more than one type: {dtypes}")
        mapping = {
            value: idx
            for idx, value in enumerate(sorted(unique_values))
        }

        metadata = {'mapping': mapping, 'dtype': next(iter(dtypes))}
        return metadata, metadata

