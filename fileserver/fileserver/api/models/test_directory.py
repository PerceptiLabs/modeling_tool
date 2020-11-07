from django.test import TestCase
import unittest
from fileserver.api.models.directory import (
        get_folder_content,
        resolve_dir,
        get_tutorial_data,
        get_drives,
        )
from fileserver.tests.utils import (
        temp_local_file,
        temp_local_dir,
        cwd,
        )
import os
import platform

BLANK_RESPONSE = {
        "current_path": "",
        "dirs": "",
        "files": "",
        "platform": platform.system(),
        }

class FolderContentsTest(TestCase):
    def test_simple_case(self):
        with temp_local_dir("first") as fd, \
             temp_local_dir(os.path.join(fd, "second")) as sd, \
             temp_local_dir(os.path.join(sd, "third")) as td, \
             temp_local_file(os.path.join(sd, "file_in_second.txt"), "abc") as f:
                r = get_folder_content(sd)
                self.assertEqual(r, {
                    'current_path': "first/second",
                    'dirs': ['third'],
                    'files': ['file_in_second.txt'],
                    'platform': platform.system()})

    def test_missing_dir(self):
        r = get_folder_content("nonexistent_dir")
        self.assertDictEqual(BLANK_RESPONSE, r)

    def test_non_dir(self):
        with temp_local_file(f"f.txt", "abc") as f:
            r = get_folder_content(f)
            self.assertEqual(BLANK_RESPONSE, r)

    @unittest.skipIf(platform.system() == "Windows", "Skipping non-windows test")
    def test_current_dir(self):
        r = get_folder_content('.')
        self.maxDiff=None
        self.assertEqual(r["current_path"], ".")
        self.assertGreater(len(r["dirs"]), 0)
        self.assertGreater(len(r["files"]), 0)

class GetDrivesTests(TestCase):
    @unittest.skipIf(platform.system() != "Windows", "Skipping windows test")
    def test_windows(self):
        resolved = get_drives()
        self.assertIn("C:", resolved)

    @unittest.skipIf(platform.system() == "Windows", "Skipping non-windows test")
    def test_posix(self):
        resolved = get_drives()
        self.assertIsNone(resolved)

class ResolveDirTests(TestCase):
    @unittest.skipIf(platform.system() == "Windows", "Skipping non-windows test")
    def test_posix(self):
        resolved = resolve_dir("~/some/dir")
        self.assertTrue(resolved.endswith("/some/dir"))
        self.assertNotIn("~",  resolved)

class TutorialDataTests(TestCase):
    def test_without_tutorials(self):
        self.assertIsNone(get_tutorial_data())

    def test_with_tutorials(self):
        with temp_local_dir("perceptilabs") as p,\
             temp_local_dir(os.path.join(p, "tutorial_data")) as t:
            expected = os.path.join(cwd(), t)
            self.assertEqual(expected, get_tutorial_data())
