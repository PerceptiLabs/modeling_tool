import logging
import os

logger = logging.getLogger(__name__)
 
class TensorflowSupportAccess:
    def __init__(self, rygg):
        self._rygg = rygg
        self.set_tfhub_env_var()

    def get_tfhub_cache_directory(self):            
        try:
            tf_hub_cache_dir = self._rygg.get_tf_hub_cache_dir()
            return tf_hub_cache_dir
        except:
            logger.exception("Failed getting dataset location")                        
            return None
    
    def set_tfhub_env_var(self):
        tf_hub_cache_dir = self.get_tfhub_cache_directory()
        os.environ['TFHUB_CACHE_DIR'] = tf_hub_cache_dir['tf_hub_cache_dir']
        return