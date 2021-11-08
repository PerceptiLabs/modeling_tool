import os
import logging
from flask.views import View

from perceptilabs.data.settings import DatasetSettings
from perceptilabs.data.base import DataLoader
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.resources.files import FileAccess
from perceptilabs.utils import get_file_path

logger = logging.getLogger(APPLICATION_LOGGER)


class BaseView(View):
    def _get_data_loader(self, settings_dict, user_email):
        dataset_settings = DatasetSettings.from_dict(settings_dict)
        csv_path = get_file_path(settings_dict)  # TODO: move one level up

        data_metadata = self._preprocessing_results_access.get_metadata(
            dataset_settings.compute_hash())
        
        file_access = FileAccess(os.path.dirname(csv_path))          
        data_loader = DataLoader.from_csv(
            file_access, csv_path, dataset_settings, metadata=data_metadata)

        return data_loader
        
        

