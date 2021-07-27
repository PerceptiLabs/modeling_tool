from flask.views import View

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
import perceptilabs.cache_utils as cache_utils


class BaseView(View):
    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        dataset_hash = cache_utils.format_key(['pipelines', user_email, dataset_settings.compute_hash()])
        data_metadata = self._data_metadata_cache.get(dataset_hash) if self._data_metadata_cache is not None else None 
        data_loader = DataLoader.from_settings(dataset_settings, metadata=data_metadata)
        return data_loader

    

