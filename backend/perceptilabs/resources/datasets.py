import os
import requests
import logging
from io import StringIO
import pandas as pd


logger = logging.getLogger(__name__)


class DatasetAccess:
    def __init__(self, rygg):
        self._rygg = rygg

    def is_perceptilabs_sourced(self, call_context, dataset_id):
        data = self._rygg.get_dataset(call_context, dataset_id)
        try:
            return bool(data["is_perceptilabs_sourced"])
        except:
            logger.exception("Failed checking if dataset is perceptilabs sourced")
            raise

    def get_location(self, call_context, dataset_id):
        data = self._rygg.get_dataset(call_context, dataset_id)

        try:
            location = data["location"].replace("\\", "/")
            logger.info(f"Found dataset {dataset_id} at {location}")
        except:
            logger.exception("Failed getting dataset location")
            raise
        else:
            return location

    def get_name(self, call_context, dataset_id):
        data = self._rygg.get_dataset(call_context, dataset_id)
        try:
            return data["name"]
        except:
            logger.exception("Failed getting dataset name")
            raise

    def get_dataframe(self, call_context, dataset_id, fix_paths_for=None):
        try:
            location = self.get_location(call_context, dataset_id)
            df = pd.read_csv(location)
            logger.info(
                f"Loaded dataframe for dataset {dataset_id}. Head:\n{df.head()}"
            )

            # Localize paths
            if fix_paths_for:
                directory = os.path.dirname(location)

                df[fix_paths_for] = df[fix_paths_for].applymap(
                    lambda rel_path: os.path.join(directory, rel_path)
                )
            return df
        except:
            logger.exception("Failed getting dataframe")
            raise
