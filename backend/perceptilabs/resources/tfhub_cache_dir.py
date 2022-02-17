import logging
import os

logger = logging.getLogger(__name__)

class TensorflowSupportAccess:
    def __init__(self, rygg):
        self._rygg = rygg

    def get_tfhub_cache_directory(self, call_context):
        return self._rygg.get_tf_hub_cache_dir(call_context)

    def set_tfhub_env_var(self, call_context):
        tf_hub_cache_dir = self.get_tfhub_cache_directory(call_context)
        os.environ['TFHUB_CACHE_DIR'] = tf_hub_cache_dir['tf_hub_cache_dir']
