import tensorflow as tf

from perceptilabs.utils import sanitize_path

class CheckpointAccess:
    def get_path(self, checkpoint_id):
        if checkpoint_id is None:
            return None
        
        checkpoint_directory = sanitize_path(checkpoint_id)        
        checkpoint_path = tf.train.latest_checkpoint(checkpoint_directory)
        return checkpoint_path
        
