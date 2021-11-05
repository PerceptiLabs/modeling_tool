from pathlib import Path
from unittest import TestCase
from unittest import skipIf
from unittest.mock import patch
import os
import platform
import shutil
import tempfile

from rygg.files import paths as target
from rygg.files.tests.utils import TempFileTester
from rygg.test_utils.timeout_decorator import timeout

TARGET="rygg.files.paths"

class TranslatePathFromUser(TempFileTester, TestCase):
    def test_simple(self):
        cases = [
            ["Local absolute path", 'local', "/a", 123, "/a"],
            ["Local from home path", 'local', "~/a/x.txt", 123, os.path.join(Path.home(), "a", "x.txt")],
            ["Local relative path", 'local', "a/b.txt", 123, os.path.join(Path.home(), "a", "b.txt")],

            ["Enterprise absolute path outside allowed", 'enterprise', "/a", 123, Exception],
            ["Enterprise absolute path inside allowed", 'enterprise', os.path.join(self.test_dir, "123", "a.txt"), 123, os.path.join(self.test_dir, "123", "a.txt")],
            ["Enterprise relative path", 'enterprise', "a/b.txt", 123, os.path.join(self.test_dir, "123", "a", "b.txt")],
        ]



        for name, ent_loc, path, project_id, expected in cases:

            is_enterprise = ent_loc == 'enterprise'
            is_linux = platform.system().lower().startswith('linux')

            # we only run enterprise on linux
            if is_enterprise and not is_linux:
                continue

            def file_upload_dir(id):
                assert id == project_id
                return os.path.join(self.test_dir, str(id))

            with self.subTest(msg=name, path=path, project_id=project_id),\
                 patch(f"{TARGET}.IS_CONTAINERIZED", is_enterprise),\
                 patch(f"{TARGET}.file_upload_dir", file_upload_dir):

                if isinstance(expected, str):
                    ret = target.translate_path_from_user(path, project_id)
                    self.assertEqual(ret, expected)
                elif issubclass(expected, Exception):
                    self.assertRaises(expected, target.translate_path_from_user, path, project_id)
                else:
                    assert False


