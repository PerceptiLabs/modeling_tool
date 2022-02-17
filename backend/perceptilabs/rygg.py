import requests
import logging

from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class RyggAdapter(ABC):
    @abstractmethod
    def get_dataset(self, call_context, dataset_id):
        raise NotImplementedError

    @abstractmethod
    def create_model(self, call_context, dataset_id, model_name, location=None):
        raise NotImplementedError

    @abstractmethod
    def load_model_json(self, call_context, model_id):
        raise NotImplementedError

    @abstractmethod
    def save_model_json(self, call_context, model_id, model):
        raise NotImplementedError

    @abstractmethod
    def get_model(self, call_context, model_id):
        raise NotImplementedError


class RyggWrapper(RyggAdapter):
    def __init__(self, base_url, file_serving_token):
        self._base_url = base_url
        self._file_serving_token = file_serving_token

    def get_dataset(self, call_context, dataset_id):
        logger.info(f"Looking for {dataset_id}")
        return self._get_json(call_context, f"/datasets/{dataset_id}/")

    def get_tf_hub_cache_dir(self, call_context):
        return self._get_json(call_context, '/tf_hub_cache_dir')

    def create_model(self, call_context, dataset_id, model_name, location=None):
        payload = {
            "name": model_name,
            "project": call_context['project_id'],
            "datasets": [dataset_id]
        }

        if location:
            payload["location"] = location

        return self._post_json(call_context, "/models/", payload)

    def load_model_json(self, call_context, model_id):
        raise NotImplementedError('Load model json not implemented!')

    def save_model_json(self, call_context, model_id, model):
        raise NotImplementedError('Save model json not implemented!')

    def get_model(self, call_context, model_id):
        return self._get_json(call_context, f"/models/{model_id}/")

    @classmethod
    def with_default_settings(cls):
        from perceptilabs.settings import RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN
        return cls(RYGG_BASE_URL, RYGG_FILE_SERVING_TOKEN)

    def _build_url(self, path, **kwargs):
        all_params = {'token': self._file_serving_token, **kwargs}
        url_params_list = [f"{k}={v}" for k,v in all_params.items()]
        url_params = "&".join(url_params_list)
        url = f"{self._base_url}{path}?{url_params}"
        return url

    def _get_json(self, call_context, path):
        try:
            url = self._build_url(path)
            res = requests.get(
                url,
                headers={'Authorization': f"Bearer {call_context['auth_token_raw']}"},
            )
            return res.json()
        except:
            logger.exception(f"Error in call to {path}")
            return {}

    def _post_json(self, call_context, path, payload):
        res = requests.post(
            self._build_url(path),
            json=payload,
            headers={'Authorization': f"Bearer {call_context['auth_token_raw']}"},
        )
        return res.json()

