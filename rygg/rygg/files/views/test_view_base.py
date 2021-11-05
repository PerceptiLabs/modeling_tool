from contextlib import contextmanager
from unittest.mock import patch
from rest_framework.test import APITestCase

def build_url(url_path, **kwargs):
    parts = [f"{k}={v}" for k,v in kwargs.items()]
    url = url_path + "?" + "&".join(f"{k}={v}" for k,v in kwargs.items())
    return url

@contextmanager
def url_with_token(url_path, **kwargs):
    with patch("rygg.middleware.settings.API_TOKEN", "thetoken"):
        yield build_url(url_path, token="thetoken", **kwargs)

class ViewTestBase(APITestCase):

    @contextmanager
    def mock_get_path_param(self, path="the_path", project_id="a_project_id", **kwargs):
        def side_effect(r):
            self.assertEqual(r.GET["path"], path)
            self.assertEqual(str(r.GET["project_id"]), str(project_id))
            return path

        with patch("rygg.files.views.util.get_path_param") as get_path_param_mock:
            get_path_param_mock.side_effect = side_effect
            yield get_path_param_mock
            get_path_param_mock.assert_called_once()


    def call(self, verb, url_path, path="the_path", project_id="a_project_id"):
        with self.mock_get_path_param(path=path, project_id=project_id):
            with url_with_token(url_path, path=path, project_id=project_id) as url:
                method = getattr(self.client, verb)
                return method(url)

    def call_and_expect_json(self, verb, url_path, expected_body, path="the_path", project_id="a_project_id"):
        response = self.call(verb, url_path, path=path, project_id=project_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.data, expected_body)
        return response

    def call_and_expect_code(self, verb, url_path, code, body=None, path="the_path", project_id="a_project_id"):
        response = self.call(verb, url_path, path=path, project_id=project_id)
        self.assertEqual(response.status_code, code)
        if body:
            self.assertEqual(response.content, body)
        return response

    def post(self, url_path, data, path="the_path", project_id="a_project_id", **other_params):
        with self.mock_get_path_param(path=path, project_id=project_id, **other_params):
            with url_with_token(url_path, path=path, project_id=project_id, **other_params) as url:
                return self.client.post(url, data, format="json")


