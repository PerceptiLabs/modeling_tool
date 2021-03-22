import tensorflow as tf


def build_categorical_pipelines(feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data

    Arguments:
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
        I.e., a tuple of the following format:
    
        (training_pipeline, validation_pipeline, postprocessing_pipeline)
    """
    categories = []  # Categories
    numericals = []  # Numericals

    idx = 0
    for tensor in feature_dataset:
        category = tensor.numpy()
        category_dtype = tensor.dtype
        
        if category not in categories:
            categories.append(category)
            numericals.append(idx)
            idx += 1
            
    categories_tensor = tf.constant(categories, dtype=category_dtype)
    numericals_tensor = tf.constant(numericals, dtype=tf.int32)    

    n_categories = len(categories)
    init = tf.lookup.KeyValueTensorInitializer(categories_tensor, numericals_tensor)
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


    init = tf.lookup.KeyValueTensorInitializer(numericals_tensor, categories_tensor)
    inv_table = tf.lookup.StaticHashTable(
        init, default_value=('<unknown>' if category_dtype is tf.string else -1)
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
        
