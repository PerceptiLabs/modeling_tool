from rygg.test_utils.timeout_decorator import timeout
from django.test import TestCase
from unittest.mock import Mock, call
from rygg.files.utils.subprocesses import CanceledError
import os
from unittest.mock import patch
import rygg.files.tasks as target
import shutil, tempfile
from rygg.files.tests import SIMPLE_ARCHIVE_NAME, SIMPLE_ARCHIVE_PATH, SIMPLE_ARCHIVE_FILES

class UnzipTaskTest(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    @timeout(0.1)
    def test_do_unzip_fails_on_missing_file(self):
        self.assertRaises(FileNotFoundError, target.do_unzip, "nonexistent", None)

    @timeout(0.1)
    def test_do_unzip_simple_case(self):

        zip = shutil.copy(SIMPLE_ARCHIVE_PATH, self.test_dir)
        expected_subdir = os.path.splitext(zip)[0]
        expected_dest_dir = os.path.join(self.test_dir, expected_subdir)

        mock = Mock()
        expected = [call(2,0, "unzipping"), call(2,2, "unzipping")]

        target.do_unzip(zip, mock.method)
        mock.method.assert_has_calls(expected)

        for fn in SIMPLE_ARCHIVE_FILES:
            path = os.path.join(expected_dest_dir, fn)
            exists = os.path.isfile(path)
            self.assertTrue(exists)

