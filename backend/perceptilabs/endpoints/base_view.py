import os
import logging
from flask.views import View

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.resources.files import FileAccess

logger = logging.getLogger(APPLICATION_LOGGER)


class BaseView(View):
    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        csv_path = settings_dict['filePath']  # TODO: move one level up
        
        key = ['pipelines', user_email, csv_path, dataset_settings.compute_hash()]

        cache = self._data_metadata_cache.for_compound_keys()
        data_metadata = cache.get(key)
        
        file_access = FileAccess(os.path.dirname(csv_path))          
        data_loader = DataLoader.from_csv(
            file_access, csv_path, dataset_settings, metadata=data_metadata)

        formatted_key = cache.put(key, data_loader.metadata)
        logger.info(f"Inserted metadata into cache (dataset key: {formatted_key})")

        return data_loader

