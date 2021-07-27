import tensorflow as tf


def is_valid_checkpoint_directory(path):
    return tf.train.latest_checkpoint(path) is not None    
    

