from pathlib import Path
from rest_framework.test import APITestCase
from rygg.files.views.test_view_base import url_with_token
import os


class TfHubCacheViewTestCase(APITestCase):
    def test_get_tf_hub_cache_dir(self):
        path = os.path.join(
            Path.home(), "Documents", "Perceptilabs", "Default", "Tensorflow_Hub_Models"
        )
        expected_body = {"tf_hub_cache_dir": path}

        with url_with_token("/tf_hub_cache_dir") as url:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.data, expected_body)
