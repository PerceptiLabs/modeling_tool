from django.test import TestCase
from threading import Event
from rygg.test_utils.timeout_decorator import timeout
import os
import shutil
import sys
import tempfile

from rygg.files.tests import SIMPLE_ARCHIVE_PATH, SIMPLE_ARCHIVE_NAME, SIMPLE_ARCHIVE_FILES
from rygg.files.utils.subprocesses import CanceledError
import rygg.files.tests as tests_module
import rygg.files.utils.zip as target

class ZipTest(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def assert_files(self, got, expected):
        got_set = set()
        expected_set = set(expected)

        for f in got:
            got_set.add(f)
            self.assertTrue(os.path.isfile(f))

        self.assertEqual(got_set, expected_set)

    @timeout(0.1)
    def test_unzipped_files_from_zipfile(self):
        num, gen = target.unzipped_files_from_zipfile(SIMPLE_ARCHIVE_PATH, dest=self.test_dir)
        self.assertEqual(num, 2)
        for f in gen:
            self.assertTrue(os.path.isfile(f))
            fn = os.path.basename(f)
            assert fn in SIMPLE_ARCHIVE_FILES

    @timeout(0.1)
    def test_unzipped_files_from_zipfile_cancels(self):
        token = Event()
        num, gen = target.unzipped_files_from_zipfile(SIMPLE_ARCHIVE_PATH, dest=self.test_dir, cancel_token=token)

        # In a two-item sequence we'll only be able to get one if we cancel via the token
        self.assertEqual(num, 2)
        gen.__next__()
        token.set()
        self.assertRaises(CanceledError, gen.__next__)

    @timeout(0.1)
    def test_unzipped_files_from_unzip_cancels(self):
        token = Event()
        num, gen = target.unzipped_files_from_unzip(SIMPLE_ARCHIVE_PATH, dest=self.test_dir, cancel_token=token)

        # In a two-item sequence we'll only be able to get one if we cancel via the token
        self.assertEqual(num, 2)
        gen.__next__()
        token.set()
        self.assertRaises(CanceledError, gen.__next__)

    @timeout(0.1)
    def test_unzipped_files_from_unzip(self):
        if sys.platform.startswith("win"):
            self.skipTest("The unzip tool is not available for Windows")

        # expect the files to be directly under the destination dir
        expected_files = [os.path.join(self.test_dir, f) for f in SIMPLE_ARCHIVE_FILES]

        # execute
        num, gen = target.unzipped_files_from_unzip(SIMPLE_ARCHIVE_PATH, dest=self.test_dir)

        # validation
        self.assertEqual(num, 2)
        self.assert_files(gen, expected_files)

    @timeout(0.1)
    def test_unzip_default_dir(self):
        if sys.platform.startswith("win"):
            self.skipTest("The unzip tool is not available for Windows")

        # Setup: copy the test zip to a directory where we can unpack it next to itself
        shutil.copy(SIMPLE_ARCHIVE_PATH, self.test_dir)
        temp_zip = os.path.join(self.test_dir, SIMPLE_ARCHIVE_NAME)

        # expect the files to be in a directory next to the temp_zip
        expected_subdir = os.path.splitext(temp_zip)[0]
        expected_files = [os.path.join(expected_subdir, f) for f in SIMPLE_ARCHIVE_FILES]

        # execute
        num, gen = target.unzipped_files_from_unzip(temp_zip)

        # validation
        self.assertEqual(num, 2)
        self.assert_files(gen, expected_files)
