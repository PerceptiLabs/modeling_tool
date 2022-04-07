import logging
import os
import perceptilabs.utils as utils

logger = logging.getLogger(__name__)


class TensorflowSupportAccess:
    def __init__(self, rygg, enable_tf_gpu_memory_growth=False):
        self._rygg = rygg
        self._enable_tf_gpu_memory_growth = enable_tf_gpu_memory_growth

    @property
    def enable_tf_gpu_memory_growth(self):
        return self._enable_tf_gpu_memory_growth

    def get_tfhub_cache_directory(self, call_context):
        try:
            tf_hub_cache_dir = self._rygg.get_tf_hub_cache_dir(call_context)
            return tf_hub_cache_dir
        except:
            logger.exception("Failed getting dataset location.")
            return None

    def set_tf_dependencies(self, call_context):
        self.set_tfhub_env_var(call_context)
        self._maybe_allow_memory_growth_on_gpus()

    def set_tfhub_env_var(self, call_context):
        try:
            tf_hub_cache_dir = self.get_tfhub_cache_directory(call_context)
            os.environ["TFHUB_CACHE_DIR"] = tf_hub_cache_dir["tf_hub_cache_dir"]
        except KeyError:
            logger.exception("Failed to set the tfhub environment variable.")

    def _maybe_allow_memory_growth_on_gpus(self):
        if self._enable_tf_gpu_memory_growth:
            try:
                utils.allow_memory_growth_on_gpus()
            except RuntimeError:
                logger.info("Memory growth already enabled.")
