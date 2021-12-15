import requests
import logging


logger = logging.getLogger(__name__)

class RyggWrapper:
    def __init__(self, base_url, file_serving_token):
        self._base_url = base_url
        self._token = file_serving_token

    def get_dataset(self, dataset_id):
        try:
            res = requests.get(
                f"{self._base_url}/datasets/{dataset_id}/?token={self._token}")
            return res.json()
        except:
            logger.exception("Error in get_dataset")
            return {}

    @classmethod
    def with_default_settings(cls):
        from perceptilabs.settings import RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN        
        return cls(RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN)
        
    
        

