import json
import os
import shutil
import tempfile
import unittest
import uuid

from rygg.files.tests.utils import TempFileTester
from rygg.files.views.test_view_base import ViewTestBase

class FileViewTestCase(TempFileTester, ViewTestBase):

    def test_head_extant_file(self):
        path = self.file_in_temp_dir()
        self.call_and_expect_code("head", "/files", 200, path=path)

    def test_head_nonexistent_file(self):
        path = self.file_in_temp_dir() + "x"
        self.call_and_expect_code("head", "/files", 404, path=path)

    def test_get_extant_file(self):
        path = self.file_in_temp_dir()
        self.call_and_expect_json("get", "/files", {"path": path}, path=path)

    def test_get_nonexistent_file(self):
        path = self.file_in_temp_dir() + "x"
        self.call_and_expect_code("get", "/files", 404, path=path)

    def test_delete_extant_file(self):
        path = self.file_in_temp_dir()
        self.assertTrue(os.path.isfile(path))

        self.call_and_expect_json("delete", "/files", {"path": path}, path=path)

        self.assertFalse(os.path.isfile(path))

    def test_delete_nonexistent_file(self):
        path = self.file_in_temp_dir() + "x"
        self.call_and_expect_code("delete", "/files", 404, path=path)
