from django.test import TestCase
from more_itertools import consume
from rygg.test_utils.timeout_decorator import timeout
import os
import requests
import shutil, tempfile

from rygg.files.utils.subprocesses import CanceledError
import rygg.files.utils.download_data as target


class DownloadTest(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    @timeout(0.1)
    def test_rejects_bad_url(self):
        def update_status(*args):
            raise NotImplementedError()

        def go():
            ret = target.download("a", self.test_dir)

        self.assertRaises(requests.exceptions.MissingSchema, go)

    @timeout(0.1)
    def test_get_data_chunks_rejects_bad_url(self):
        self.assertRaises(requests.exceptions.MissingSchema, target.get_data_chunks, "badurl")

    @timeout(0.1)
    def test_write_chunks_makes_subdirs(self):
        # setup
        empty_generator = iter([b"content"])
        subdirs = ["a", "b"]
        dest_dir = os.path.join(self.test_dir, *subdirs)
        dest_filename = "emptyfile"
        expected_file = os.path.join(dest_dir, dest_filename)

        # execute
        written = target.write_chunks(empty_generator, expected_file)
        consume(written)

        # check
        self.assertTrue(os.path.isfile(expected_file))

    @timeout(0.1)
    def test_write_chunks_does_not_make_subdirs_for_no_data(self):
        # setup
        empty_generator = iter([])
        subdirs = ["a", "b"]
        dest_dir = os.path.join(self.test_dir, *subdirs)
        dest_filename = "emptyfile"
        expected_file = os.path.join(dest_dir, dest_filename)

        # execute
        written = target.write_chunks(empty_generator, expected_file)
        consume(written)

        # check
        self.assertFalse(os.path.isfile(expected_file))

    @timeout(0.1)
    def test_write_chunks_writes_binary(self):
        chunk = b'\xff\xfeG\x00e\x00e\x00k\x00'
        chunks = iter([chunk])
        expected_filename = os.path.join(self.test_dir, "simplefile")

        written = target.write_chunks(chunks, expected_filename)
        consume(written)

        content = open(expected_filename, "rb").read()
        self.assertEqual(content, chunk)
