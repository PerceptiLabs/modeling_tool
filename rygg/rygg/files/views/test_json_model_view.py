import json
import os

from rygg.files.views.test_view_base import ViewTestBase
from rygg.files.tests.utils import TempFileTester


class JsonModelViewTests(TempFileTester, ViewTestBase):
    def test_get_extant_by_full_path(self):
        content = {"this": "is content"}
        path = self.file_in_temp_dir(filename="model.json", content=json.dumps(content))
        expected_body = {
            "model_body": content,
            "path": path
        }
        self.call_and_expect_json("get", "/json_models", expected_body, path=path)

    def test_get_extant_by_parent_dir_path(self):
        content = {"this": "is content"}
        path = self.file_in_temp_dir(filename="model.json", content=json.dumps(content))
        expected_body = {
            "model_body": content,
            "path": path
        }
        parent_dir = os.path.dirname(path)

        self.call_and_expect_json("get", "/json_models", expected_body, path=path)

    def test_get_nonexistent_by_full_path(self):
        content = {"this": "is content"}
        path = self.file_in_temp_dir(filename="model.json", content=json.dumps(content))
        parent_dir = os.path.dirname(path)+"x"
        nonexistent_path = os.path.join(parent_dir, "model.json")

        self.call_and_expect_code("get", "/json_models", 404, path=nonexistent_path)

    def test_get_nonexistent_by_parent_dir_path(self):
        content = {"this": "is content"}
        path = self.file_in_temp_dir(filename="model.json", content=json.dumps(content))
        nonexistent_parent_dir = os.path.dirname(path) + "x"

        self.call_and_expect_code("get", "/json_models", 404, path=nonexistent_parent_dir)

    def test_get_non_json_by_full_path(self):
        path = self.file_in_temp_dir(filename="model.json", content="non json")
        self.call_and_expect_code("get", "/json_models", 204, path=path)

    def test_get_non_json_by_parent_dir_path(self):
        path = self.file_in_temp_dir(filename="model.json", content="non json")
        parent_dir = os.path.dirname(path)
        self.call_and_expect_code("get", "/json_models", 204, path=parent_dir)

    def test_post_valid_by_full_path(self):
        content = {"this": "is content"}
        path = self.filename_in_temp_dir(os.path.join("some_model", "model.json"))

        response = self.post("/json_models", content, path=path)

        self.assertEqual(response.data, {"path": path})
        self.assertTrue(os.path.isfile(path))

    def test_post_valid_by_parent_dir_path(self):
        content = {"this": "is content"}
        path = self.filename_in_temp_dir("some_model")

        response = self.post("/json_models", content, path=path)

        expected_path = os.path.join(path, "model.json")
        self.assertEqual(response.data, {"path": expected_path})
        self.assertTrue(os.path.isfile(expected_path))
