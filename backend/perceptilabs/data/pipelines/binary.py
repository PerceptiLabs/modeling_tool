import tensorflow as tf


def build_binary_pipelines(feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data of type binary

    Arguments:
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
        I.e., a tuple of the following format:
    
        (training_pipeline, validation_pipeline, postprocessing_pipeline)
    """
    class Pipeline(tf.keras.Model):
        def call(self, x):
            init = None

            # Build out valid keys and corresponding values depending on input type
            if x.dtype == tf.string:
                keys_tensor = tf.constant(['True', 'true', 'False', 'false'])
                values_tensor = tf.constant([1.0, 1.0, 0.0, 0.0])
                init = tf.lookup.KeyValueTensorInitializer(keys_tensor, values_tensor)
            elif x.dtype == tf.int32 or x.dtype == tf.bool:
                x = tf.cast(x, tf.int32)
                keys_tensor = tf.constant([1, 0])
                values_tensor = tf.constant([1.0, 0.0])
                init = tf.lookup.KeyValueTensorInitializer(keys_tensor, values_tensor)
            else:
                raise ValueError("Invalid Binary inputs")

            # Look up values that matches the input
            table = tf.lookup.StaticHashTable(init, default_value=0)
            x = table.lookup(x)

            return x

    return Pipeline(), None, None
        
