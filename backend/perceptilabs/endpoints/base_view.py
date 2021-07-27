import logging
from flask.views import View

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
import perceptilabs.caching.utils as cache_utils
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class BaseView(View):
    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        dataset_hash = cache_utils.format_key(['pipelines', user_email, dataset_settings.compute_hash()])
        logger.info(f"Computed dataset hash: {dataset_hash}")

        data_metadata = None
        if self._data_metadata_cache is not None:
            data_metadata = self._data_metadata_cache.get(dataset_hash)
        
        data_loader = DataLoader.from_settings(dataset_settings, metadata=data_metadata)

        if self._data_metadata_cache is not None:
            self._data_metadata_cache[dataset_hash] = data_loader.metadata            
            logger.info(f"Inserted metadata into cache (dataset hash: {dataset_hash})")

        return data_loader

    

