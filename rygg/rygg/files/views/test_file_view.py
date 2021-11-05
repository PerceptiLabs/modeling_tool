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

    def test_get_file_content_on_extant_file(self):
        path = self.file_in_temp_dir()
        self.call_and_expect_json("get", "/files/get_file_content", {"file_contents": ["this is some text"]}, path=path)

    def test_get_file_content_on_nonexistent_file(self):
        path = self.file_in_temp_dir() + "x"
        self.call_and_expect_code("get", "/files/get_file_content", 404, path=path)

    def test_get_file_content_with_invalid_unicode(self):
        INVALID_UTF=b"text,label\nFreeMsg Hey there darling it's been 3 week's now and no word back! I'd like some fun you up for it still? Tb ok! std chgs to send \xc3\xa5\xc2\xa31.50 to rcv,spam\n"
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(INVALID_UTF)
            f.close()
            resp = self.call_and_expect_code("get", f"/files/get_file_content", 200, path=f.name)
            content = resp.data['file_contents']
            line = content[1]
            self.assertIn("std chgs", line)
