from django.test import TestCase
from fileserver.api.models.directory import get_folder_content
from fileserver.tests.utils import (
        temp_local_file,
        temp_local_dir,
        )
import os
import platform

class FolderContentsTest(TestCase):
    def test_simple_case(self):
        with temp_local_dir("first") as fd, \
             temp_local_dir(f"{fd}/second") as sd, \
             temp_local_dir(f"{sd}/third") as td, \
             temp_local_file(f"{sd}/file_in_second.txt", "abc") as f:
                r = get_folder_content(sd)
                self.assertEqual(r, {
                    'current_path': 'first/second',
                    'dirs': ['third'],
                    'files': ['file_in_second.txt'],
                    'platform': platform.system()})

    def test_missing_dir(self):
        r = get_folder_content("nonexistent_dir")
        self.assertEqual(r, None)

    def test_non_dir(self):
        with temp_local_file(f"f.txt", "abc") as f:
            def run():
                get_folder_content(f)

            self.assertRaises(ValueError, run)


    # windows-specific test
    def test_windows_root(self):
        if platform.system() != "Windows":
            return

        r = get_folder_content("/")
        self.assertEqual(r['current_path'], '/')
        as_lower = [d.lower() for d in r["dirs"]]
        self.assertTrue("c:" in as_lower)
        self.assertEqual(r['platform'], "Windows")
