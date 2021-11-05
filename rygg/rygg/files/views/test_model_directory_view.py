import os

from rygg.files.views.test_view_base import ViewTestBase
from rygg.files.tests.utils import TempFileTester

class ModelDirectoryTestCase(TempFileTester, ViewTestBase):
    def test_get_good(self):
        path = self.file_in_temp_dir()
        req_path = os.path.dirname(path)
        self.call_and_expect_json("get", "/modeldirectories", {"path": req_path}, path=req_path)
        self.call_and_expect_code("head", "/modeldirectories", 200, path=req_path)

    def test_get_missing(self):
        self.call_and_expect_code("head", "/modeldirectories", 404, path="nonexistent")
        self.call_and_expect_code("get", "/modeldirectories", 404, path="nonexistent")

    def test_get_non_dir(self):
        path = self.file_in_temp_dir()
        self.call_and_expect_code("get", "/modeldirectories", 400, path=path)
        self.call_and_expect_code("head", "/modeldirectories", 400, path=path)

class ModelDirectoryTreeTestCase(TempFileTester, ViewTestBase):
    def test_get_good(self):
        path = self.file_in_temp_dir()
        req_path = os.path.dirname(path)
        expected = {
            "contents": [
                {"path": path, "size": 17}
            ],
            "page": 1,
            "path": req_path,
        }
        self.call_and_expect_json("get", "/modeldirectories/tree", expected, path=req_path)

    def test_get_missing(self):
        self.call_and_expect_code("get", "/modeldirectories/tree", 204, path="nonexistent")

    def test_get_non_dir(self):
        path = self.file_in_temp_dir()
        self.call_and_expect_code("get", "/modeldirectories/tree", 400, path=path)

