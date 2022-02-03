import requests
import logging

from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RyggAdapter(ABC):
    @abstractmethod
    def get_dataset(self, dataset_id):
        raise NotImplementedError

    @abstractmethod    
    def create_model(self, project_id, dataset_id, model_name, location=None):
        raise NotImplementedError

    @abstractmethod    
    def load_model_json(self, model_id):
        raise NotImplementedError

    @abstractmethod    
    def save_model_json(self, model_id, model):
        raise NotImplementedError

    @abstractmethod
    def get_model(self, model_id):
        raise NotImplementedError


class RyggWrapper(RyggAdapter):
    def __init__(self, base_url, file_serving_token):
        self._base_url = base_url
        self._token = file_serving_token

    def get_dataset(self, dataset_id):
        logger.info(f"Looking for {dataset_id}")
        try:
            res = requests.get(
                f"{self._base_url}/datasets/{dataset_id}/?token={self._token}")
            return res.json()
        except:
            logger.exception(f"Error in get_dataset for dataset {dataset_id}")
            raise

    def create_model(self, project_id, dataset_id, model_name, location=None):
        payload = {
            "name": model_name,
            "project": project_id,
            "datasets": [dataset_id]
        }

        if location:
            payload["location"] = location
        
        res = requests.post(
            f"{self._base_url}/models/?token={self._token}",
            json=payload
        )
        return res.json()

    def load_model_json(self, model_id):
        raise NotImplementedError('Load model json not implemented!')

    def save_model_json(self, model_id, model):
        raise NotImplementedError('Save model json not implemented!')        

    def get_model(self, model_id):
        try:
            res = requests.get(
                f"{self._base_url}/models/{model_id}/?token={self._token}")
            return res.json()
        except:
            logger.exception("Error in get_model")
            return {}
    
    @classmethod
    def with_default_settings(cls):
        from perceptilabs.settings import RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN        
        return cls(RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN)
        
    
        

