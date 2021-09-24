from django.test import TestCase
import os
import shutil, tempfile

import rygg.files.tasks as target
from rygg.files.tests import SIMPLE_ARCHIVE_PATH
from rygg.test_utils.timeout_decorator import timeout


class UnzipTaskTest(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @timeout(0.1)
    def test_unzip_fails_on_missing_file(self):
        def run():
            statuses = target.unzip(None, "nonexistent")
            # consume the statuses
            unzipped = list(list(statuses)[-1])

        self.assertRaises(FileNotFoundError, run)
