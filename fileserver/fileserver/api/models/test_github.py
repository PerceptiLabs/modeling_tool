from django.test import TestCase
from unittest.mock import patch, Mock
from fileserver.tests.utils import (
        temp_local_file,
        temp_local_dir,
        )
from fileserver.api.models.github import (
        export_repo_basic,
        export_repo_advanced,
        import_repo
        )
import os

class BuildExportTests(TestCase):
    def test_simple(self):
        mock = Mock()
        with temp_local_dir("the_dir") as d:
            export_repo_basic(mock, d, False, [], commit_message="msg")
            expected = {
                    os.path.join(d, "README.md"): "README.md",
                    os.path.join(d, "pl_logo.png"): "pl_logo.png",
                    }
            mock.add_files.assert_called_once_with(expected, "msg")

    def test_advanced(self):
        mock = Mock()
        with temp_local_dir("the_dir") as d:
            export_repo_advanced(mock, d, [], [], [], commit_message="advanced msg")
            expected = {
                    os.path.join(d, "README.md"): "README.md",
                    os.path.join(d, "pl_logo.png"): "pl_logo.png",
                    }
            mock.add_files.assert_called_once_with(expected, "advanced msg")

    # TODO: many more test cases


class BuildImportTests(TestCase):
    def test_simple(self):
        with temp_local_dir("the_dir") as d,\
             patch("fileserver.api.models.github.RepoImporterAPI") as api_class_mock:

            api_mock = api_class_mock.return_value
            api_mock.is_repo_public.return_value = True
            api_mock.model_exist.return_value = False

            import_repo(d, "http://noop")
            expected = os.path.join(d, "noop")
            api_mock.clone_to.assert_called_once_with(expected)

    # TODO: many more test cases
