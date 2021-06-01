import tensorflow as tf

from perceptilabs.data.pipelines.base import PipelineBuilder


class CategoricalPipelineBuilder(PipelineBuilder):
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

        n_categories, categories_tensor, indices_tensor = self._get_categories_and_indices(feature_dataset)
        
        init = tf.lookup.KeyValueTensorInitializer(categories_tensor, indices_tensor)
        table = tf.lookup.StaticHashTable(init, default_value=-1)  # TODO(anton.k): the hash table approach should be removed w/ tf 2.4: keras preprocessing is better (and can be inverted easily)
                
    
        class TrainingPipeline(tf.keras.Model):
            def __init__(self, lookup_table, n_categories):
                super().__init__()
                self._lookup_table = lookup_table
                self.n_categories = n_categories
            
            def call(self, x):
                x = self._lookup_table.lookup(x)
                x = tf.one_hot(x, self.n_categories)          
                return x
    
    
        init = tf.lookup.KeyValueTensorInitializer(indices_tensor, categories_tensor)
        inv_table = tf.lookup.StaticHashTable(
            init, default_value=('<unknown>' if categories_tensor.dtype is tf.string else -1)
        )  # TODO(anton.k): the hash table approach should be removed w/ tf 2.4: keras preprocessing is better (and can be inverted easily)
        
        class PostprocessingPipeline(tf.keras.Model):
            def __init__(self, lookup_table):
                super().__init__()
                self._lookup_table = lookup_table
            
            def call(self, x):
                x = tf.argmax(x) # Convert from one-hot encoded values
                x = tf.cast(x, tf.int32)
                x = self._lookup_table.lookup(x)
                return x 
    
        return TrainingPipeline(table, n_categories), None, PostprocessingPipeline(inv_table)
            
    
    def _get_categories_and_indices(self, feature_dataset):
        """ Loops over the dataset and maps values to an index (e.g., cat -> 0) """
    
        categories = []  # Categories
        numericals = []  # Numericals
        indices = []  # Indices
    
        idx = 0
        for tensor in feature_dataset:
            category = tensor.numpy()
            category_dtype = tensor.dtype
            
            if category not in categories:
                categories.append(category)
                indices.append(idx)
                try:
                    numericals.append(int(category))
                except:
                    pass
                    
                idx += 1
    
        if len(numericals) == len(indices):
            indices = numericals  # All values could be cast to numerical.
    
        categories_tensor = tf.constant(categories, dtype=category_dtype)
        indices_tensor = tf.constant(indices, dtype=tf.int32)
    
        n_categories = len(categories)
        
        return n_categories, categories_tensor, indices_tensor
    
