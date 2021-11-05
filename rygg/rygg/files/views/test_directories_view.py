import os
import platform
import unittest
import uuid

from rygg.files.tests.utils import TempFileTester, temp_local_dir, cwd
from rygg.files.views.test_view_base import ViewTestBase, url_with_token

def random_str():
    return str(uuid.uuid4())

class TutorialDataTestCase(TempFileTester, ViewTestBase):

    def test_get_missing_tutorial_data(self):
        with url_with_token("/directories/tutorial_data") as url:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 204)

    def test_get_extant_tutorial_data(self):
        with temp_local_dir("perceptilabs") as p,\
             temp_local_dir(os.path.join(p, "tutorial_data")) as d,\
             url_with_token("/directories/tutorial_data") as url:
            expected = os.path.join(cwd(), d)
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"path": expected})


class DirectoriesViewTestCase(TempFileTester, ViewTestBase):

    def test_get_directories(self):
        self.call_and_expect_json("get", "/directories", {"path": self.test_dir}, path=self.test_dir)

    def test_head_directories(self):
        self.call_and_expect_code("head", "/directories", 200, path=self.test_dir)

    def test_post_directories(self):
        path = os.path.join(self.test_dir, random_str())

        response = self.post("/directories", {}, path=path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'path': path})
        self.assertTrue(os.path.isdir(path))

    def test_delete_directories(self):
        d = os.path.join(self.test_dir, random_str())
        os.makedirs(d)
        self.assertTrue(os.path.isdir(d))

        response = self.call_and_expect_code("delete", "/directories", 200, path=d)
        self.assertEqual(response.data, {'path': d})

class DrivesTestCase(ViewTestBase):

    @unittest.skipIf(platform.system() == "Windows", "Skipping windows test")
    def test_get_drives_posix(self):
        with url_with_token("/directories/drives") as url:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 204)

    @unittest.skipUnless(platform.system() == "Windows", "Skipping non-windows test")
    def test_get_drives_win(self):
        with url_with_token("/directories/drives") as url:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("C:", response.data["drives"])
