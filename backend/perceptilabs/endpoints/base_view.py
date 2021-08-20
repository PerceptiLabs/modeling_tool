import logging
from flask.views import View

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class BaseView(View):
    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)

        key = ['pipelines', user_email, dataset_settings.compute_hash()]

        cache = self._data_metadata_cache.for_compound_keys()
        data_metadata = cache.get(key)

        data_loader = DataLoader.from_settings(dataset_settings, metadata=data_metadata)

        formatted_key = cache.put(key, data_loader.metadata)
        logger.info(f"Inserted metadata into cache (dataset key: {formatted_key})")

        return data_loader

