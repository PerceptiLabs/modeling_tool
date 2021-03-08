import tensorflow as tf


def build_image_pipelines(feature_dataset: tf.data.Dataset = None) -> tf.keras.Model:
    """ Returns a keras model for preprocessing data

    Arguments:
        feature_dataset: optional. Can be used for invoking .adapt() on keras preprocessing layers.
    Returns:
        Two pipelines (tf.keras.Model) for training and inference. One for postprocessing.
        I.e., a tuple of the following format:
    
        (training_pipeline, validation_pipeline, postprocessing_pipeline)
    """
    class Pipeline(tf.keras.Model):
        def call(self, x):
            x = tf.io.read_file(x)
            x = tf.io.decode_image(x)
            x = tf.cast(x, dtype=tf.float32)
            return x

    return Pipeline(), None, None
        
