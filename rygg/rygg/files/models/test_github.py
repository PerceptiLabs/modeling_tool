from django.test import TestCase
from unittest.mock import patch, Mock
import os

import rygg.files.models.github as target
from rygg.files.tests.utils import TempFileTester
from rygg.test_utils.timeout_decorator import timeout


def create_readme(path):
    open(os.path.join(path, "README.md"), "w").write("text")
    open(os.path.join(path, "pl_logo.png"), "w").write("text")


@patch("rygg.files.interfaces.github_export.RepoExporterAPI")
@patch("rygg.files.models.github._create_README")
class BuildExportTests(TempFileTester, TestCase):
    @timeout(10)
    def test_simple(self, create_readme_mock, mock_exporter_api):
        create_readme_mock.side_effect = create_readme
        expected = {
            os.path.join(self.test_dir, "README.md"): "README.md",
            os.path.join(self.test_dir, "pl_logo.png"): "pl_logo.png",
        }
        m = Mock()
        mock_exporter_api.return_value = m

        target.export_repo_basic(
            "the token", "repo name", self.test_dir, False, [], commit_message="msg"
        )

        mock_exporter_api.assert_called_once_with("the token", "repo name")
        m.add_files.assert_called_once_with(expected, "msg")

    @timeout(10)
    def test_advanced(self, create_readme_mock, mock_exporter_api):
        create_readme_mock.side_effect = create_readme
        expected = {
            os.path.join(self.test_dir, "README.md"): "README.md",
            os.path.join(self.test_dir, "pl_logo.png"): "pl_logo.png",
        }
        m = Mock()
        mock_exporter_api.return_value = m

        target.export_repo_advanced(
            "the token",
            "repo name",
            self.test_dir,
            [],
            [],
            [],
            commit_message="advanced msg",
        )

        mock_exporter_api.assert_called_once_with("the token", "repo name")
        m.add_files.assert_called_once_with(expected, "advanced msg")

    # TODO: many more test cases


@patch("rygg.files.interfaces.github_import.RepoImporterAPI")
class BuildImportTests(TempFileTester, TestCase):
    @timeout(0.1)
    def test_simple(self, mock_importer_api):
        api_mock = Mock()
        api_mock.is_repo_public.return_value = True
        api_mock.model_exist.return_value = False

        mock_importer_api.return_value = api_mock

        target.import_repo(self.test_dir, "http://noop")

        expected = os.path.join(self.test_dir, "noop")
        api_mock.clone_to.assert_called_once_with(expected)

    # TODO: many more test cases


@patch("rygg.files.interfaces.github_issue.CreateIssueAPI")
class BuildIssueTests(TempFileTester, TestCase):
    @timeout(0.1)
    def test_simple(self, mock_api_class):
        api_mock = Mock()
        # api_mock.is_repo_public.return_value = True
        # api_mock.model_exist.return_value = False

        mock_api_class.return_value = api_mock

        target.create_issue("github token", "issue type", "the title", "the body")

        api_mock._create_issue.assert_called_once_with("the title", "the body")

    # TODO: many more test cases
