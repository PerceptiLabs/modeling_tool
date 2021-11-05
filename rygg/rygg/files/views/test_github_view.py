from unittest.mock import patch, Mock
import json
import os

from rygg.api.models import Project
from rygg.files.views.test_view_base import ViewTestBase, url_with_token
from rygg.files.tests.utils import TempFileTester

PROJECT_ID=None
def setUpModule():
    global PROJECT_ID

    p = Project()
    p.save()
    PROJECT_ID=p.project_id

def tearDownModule():
    Project.objects.filter(pk=PROJECT_ID).delete()


@patch("rygg.files.models.github.import_repo", return_value=None)
@patch("rygg.files.paths.translate_path_from_user")
class GithubImportTestCase(TempFileTester, ViewTestBase):

    def test_url_required(self, translate_mock, import_repo_mock):
        resp = self.post("/github/import", {}, self.test_dir)
        self.assertEqual(resp.status_code, 400)
        import_repo_mock.assert_not_called()

    def test_simple_case(self, translate_mock, import_repo_mock):
        expected = {"path": self.test_dir}
        response = self.post("/github/import", {}, self.test_dir, url="http://noop")
        import_repo_mock.assert_called_once_with(self.test_dir, "http://noop", overwrite=False)

@patch("rygg.files.paths.translate_path_from_user")
class GithubExportTestCase(TempFileTester, ViewTestBase):

    def test_basic(self, translate_mock):
        request = {
            "github_token": "gh_token",
            "model_path": "the_model_path",
            "repo_name": "the_repo_name",
            "file_list": [],
            "data_path": ["some/path"],
            "commit_message": "first commit",
            "export_type": "basic",
        }
        translate_mock.return_value = "translated_path"
        with patch("rygg.files.models.github.export_repo_basic", return_value=["2341234", "the_url"]) as export_mock:

            response = self.post("/github/export", request, path=self.test_dir, project_id=PROJECT_ID)
            self.assertEqual(response.data, {"sha": "2341234", "URL": "the_url"})
            self.assertEqual(response.status_code, 200)
            export_mock.assert_called_once_with('gh_token', 'the_repo_name', self.test_dir, False, ['translated_path'], commit_message='first commit')


        translate_mock.assert_called_once_with('some/path', PROJECT_ID)

    def test_advanced(self, translate_mock):
        request = {
            "github_token": "gh_token",
            "model_path": "the_model_path",
            "repo_name": "the_repo_name",
            "file_list": [],
            "data_path": ["some/path"],
            "commit_message": "first commit",
            "export_type": "advanced",
            "datafiles": [
                "d", "e"
            ],
            "tensorfiles": [
                "a", "b", "c"
            ],
        }
        translate_mock.return_value = "translated_path"
        with patch("rygg.files.models.github.export_repo_advanced", return_value=["2341234", "the_url"]) as export_mock:

            response = self.post("/github/export", request, path=self.test_dir, project_id=PROJECT_ID)
            self.assertEqual(response.data, {"sha": "2341234", "URL": "the_url"})
            self.assertEqual(response.status_code, 200)
            export_mock.assert_called_once_with('gh_token', 'the_repo_name', self.test_dir, request['tensorfiles'], request['datafiles'], ['translated_path'], commit_message='first commit')

        translate_mock.assert_called_once_with('some/path', PROJECT_ID)

class GithubIssueTests(ViewTestBase):
    def test_simple(self):
        request = {
            "github_token": "gh_token",
            "issue_type": "the issue type",
            "body": "the issue body",
            "title": "the issue title",
        }
        with patch("rygg.files.models.github.create_issue", return_value="the issue number"):
            with url_with_token("/github/issue") as url:
                response = self.client.post(url, json.dumps(request), content_type="application/json")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, {"Issue Number": "the issue number"})
