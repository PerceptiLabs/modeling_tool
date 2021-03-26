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

    # NOTE: Use the dataset directly to get the shape
    # Store the shape in the Pipeline 
    tensor = next(iter(feature_dataset))
    image_encoded = tf.io.read_file(tensor)
    image_decoded = tf.io.decode_image(image_encoded)
    shape = image_decoded.shape


    class Pipeline(tf.keras.Model):
        def __init__(self):
            super().__init__()
            self.image_shape = shape

        def call(self, x):
            x = tf.io.read_file(x)
            x = tf.io.decode_image(x)
            x = tf.cast(x, dtype=tf.float32)
            return x

    return Pipeline(), None, None
        
