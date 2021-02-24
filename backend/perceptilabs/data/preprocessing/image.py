import tensorflow as tf


def build_image_pipeline(feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data

    Arguments:
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        a tf.keras.Model
    """
    class Pipeline(tf.keras.Model):
        def call(self, x):
            x = tf.io.read_file(x)
            x = tf.io.decode_image(x)
            x = tf.cast(x, dtype=tf.float32)
            return x
        
    return Pipeline()        
        
