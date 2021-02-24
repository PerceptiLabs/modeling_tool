import tensorflow as tf


def build_numerical_pipeline(self, feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data

    Arguments:
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        a tf.keras.Model
    """        
    class Pipeline(tf.keras.Model):
        def call(self, x):
            return tf.cast(x, dtype=tf.float32)
        
    return Pipeline()        
        
