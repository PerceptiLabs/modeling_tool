from unittest.mock import patch, Mock
from django.test import TestCase
import unittest
from django_http_exceptions import HTTPExceptions
from fileserver.api.views.file_view import FileView
from fileserver.api.views.directory_view import (
        DirectoryView,
        get_tutorial_data,
        get_drives,
        )
from fileserver.api.views.json_model_view import JsonModelView
from fileserver.api.views.model_directory_view import (modeldirectory_tree, get_modeldirectory)
from fileserver.api.views.github_view import (github_export, github_import)
from fileserver.tests.utils import (
        temp_local_file,
        temp_local_dir,
        local_file_cleanup,
        temp_json_file,
        local_dir_cleanup,
        cwd,
        )
from rest_framework.test import APIRequestFactory, APIClient
import json
import os
import platform


class SettingsTest(TestCase):
    EXPECTED_HOSTS = set(["127.0.0.1", "localhost"])

    def test_allowed_hosts(self):
        from fileserver.settings import ALLOWED_HOSTS

        l = set(ALLOWED_HOSTS)
        self.assertSetEqual(l, self.EXPECTED_HOSTS)


class TestCaseBase(TestCase):
    def build_request(self, method_name, path, body=None):
        self.factory = APIRequestFactory()
        method = getattr(self.factory, method_name)
        return method(path, body, format="json") if body else method(path)

    def build_call(self, method_name, path, body=None):
        request = self.build_request(method_name, path, body=body)
        view = self.VIEW_CLASS.as_view()

        def do_call():
            return view(request)

        return do_call

    def call_and_expect_code(self, method_name, path, code, body=None):
        call = self.build_call(method_name, path, body=body)
        response = call()
        self.assertEqual(response.status_code, code)
        return response

    def call_and_expect_body(self, method_name, path, expected_body):
        call = self.build_call(method_name, path)
        response = call()
        self.assertEqual(response.status_code, 200)
        as_dict = json.loads(response.content)
        self.maxDiff=None
        self.assertDictEqual(as_dict, expected_body)
        return response

    def call_and_expect_error(self, method_name, path, error_class):
        call = self.build_call(method_name, path)
        self.assertRaises(error_class, call)


class MethodViewWrapper:
    def __init__(self, method):
        self.method = method

    def as_view(self):
        return self.method


class FileViewTestCase(TestCaseBase):
    VIEW_CLASS = FileView

    def test_get_files(self):
        with temp_local_file("testfile123.txt", "content") as name:
            response = self.call_and_expect_code("get", f"/files?path={name}", 200)
            self.assertEqual(json.loads(response.content), {"path": name})

    def test_head_files(self):
        with temp_local_file("testfile123.txt", "content") as name:
            response = self.call_and_expect_code("head", f"/files?path={name}", 200)
            self.assertEqual(json.loads(response.content), {"path": name})

    def test_get_files_with_missing_path(self):
        self.call_and_expect_error("get", f"/files", HTTPExceptions.BAD_REQUEST)

    # This only works if there's a home directory
    @unittest.skipIf("~" in os.path.expanduser("~"), "There's no home directory")
    def test_path_resolution_for_existing_file(self):
        def get_a_home_dir_file():
            import itertools
            home = os.path.expanduser("~")
            home_walk = os.walk(home)
            home_root_level = itertools.islice(home_walk, 1)
            _,_,files = list(home_root_level)[0]
            return [f for f in files if not f[0] == "."][0]

        request_path = os.path.join("~", get_a_home_dir_file())

        response = self.call_and_expect_code("head", f"/files?path={request_path}", 200)

    # This only works if there's a home directory
    @unittest.skipIf("~" in os.path.expanduser("~"), "There's no home directory")
    def test_path_resolution_for_nonexistent_file(self):
        import secrets
        request_path = os.path.join("~", "{secrets.token_urlsafe()}")
        response = self.call_and_expect_error("head", f"/files?path={request_path}", HTTPExceptions.NO_CONTENT)


class DirectoriesViewTestCase(TestCaseBase):
    VIEW_CLASS = DirectoryView

    def test_get_directories(self):
        with temp_local_dir("testing123") as d:
            req_path = os.path.join(os.getcwd(), d)
            self.call_and_expect_code("get", f"/directories?path={req_path}", 200)

    def test_head_directories(self):
        with temp_local_dir("testing123") as d:
            req_path = os.path.join(os.getcwd(), d)
            self.call_and_expect_code("head", f"/directories?path={req_path}", 200)

    def test_post_directories(self):
        with local_dir_cleanup("testing123") as d:
            req_path = os.path.join(os.getcwd(), d)
            self.call_and_expect_code("post", f"/directories?path={req_path}", 200)
            assert os.path.isdir("testing123"), f"expected post /directories to create file testing123"

    def test_delete_directories(self):
        with temp_local_dir("to_delete") as d:
            req_path = os.path.join(os.getcwd(), d)
            self.assertTrue(os.path.isdir(d), "the directory wasn't set up")
            self.call_and_expect_code("delete", f"/directories?path={req_path}", 200)
            self.assertFalse(os.path.isdir(d), "the directory wasn't set up")

class TutorialDataTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(get_tutorial_data)

    def test_get_missing_tutorial_data(self):
        self.call_and_expect_error("get", "", HTTPExceptions.NO_CONTENT)

    def test_get_extant_tutorial_data(self):
        with temp_local_dir("perceptilabs") as p,\
             temp_local_dir(os.path.join(p, "tutorial_data")) as d:
            expected = os.path.join(cwd(), d)
            self.call_and_expect_body("get", "", {"path": expected})


class DrivesTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(get_drives)

    @unittest.skipIf(platform.system() == "Windows", "Skipping windows test")
    def test_get_drives(self):
        self.call_and_expect_error("get", "", HTTPExceptions.NO_CONTENT)

    @unittest.skipUnless(platform.system() == "Windows", "Skipping non-windows test")
    def test_get_drives(self):
        self.call_and_expect_body("get", "", {"drives": ["C:"]})

class JsonModelsViewTestCase(TestCaseBase):
    VIEW_CLASS = JsonModelView

    def test_get_json_models(self):
        with temp_json_file("test_model.json", {"this": "is json", "and this is a number": 123}) as test_file:
            resp = self.call_and_expect_code("get", f"/json_models?path={test_file}", 200)
            as_dict = json.loads(resp.content)
            if as_dict["path"] != test_file:
                raise exception(f"get /json_models didn't populate the path in the response body")
            if as_dict["model_body"]["this"] != "is json":
                raise exception(f"get /json_models didn't populate the json body correctly")

    def test_get_json_models_with_non_json(self):
        with temp_local_file("test_non_model.txt", "this is text") as test_file:
            self.call_and_expect_error("get", f"/json_models?path={test_file}", HTTPExceptions.NO_CONTENT)

    def test_post_json_models(self):
        req = {"this": "is json"}
        test_file = os.path.join(os.getcwd(), "testing123.json")
        with local_file_cleanup(test_file) as f:
            self.call_and_expect_code("post", f"/json_models?path={f}", 200, body=req)
            self.assertTrue(os.path.exists(f), f"expected post /json_models to create the file {f}")

    def test_post_json_models_with_non_json(self):
        with local_file_cleanup("testing123.json") as f:
            cur_url = f"/json_models?path={f}"
            self.call_and_expect_error("post", cur_url, HTTPExceptions.BAD_REQUEST)
            self.assertFalse(os.path.exists(f), f"expected post /json_models to not create an invalid json file")


class ModelDirectoryTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(get_modeldirectory)

    def test_get_good(self):
        with temp_local_dir("testing123") as d:
            with temp_local_file(os.path.join(d, "test_non_model.txt"), "this is text") as test_file:
                req_path = os.path.join(os.getcwd(), d)
                self.call_and_expect_code("get", f"?path={req_path}", 200)
                self.call_and_expect_code("head", f"?path={req_path}", 200)

    def test_get_missing(self):
        self.call_and_expect_error("get", f"?path=nonexistent", HTTPExceptions.NO_CONTENT)
        self.call_and_expect_error("head", f"?path=nonexistent", HTTPExceptions.NO_CONTENT)

    def test_get_non_dir(self):
        with temp_local_file(f"some.txt", "this is text") as test_file:
            self.call_and_expect_error("get", f"?path={test_file}", HTTPExceptions.BAD_REQUEST)
            self.call_and_expect_error("head", f"?path={test_file}", HTTPExceptions.BAD_REQUEST)

class ModelDirectoryTreeTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(modeldirectory_tree)

    def test_get_good(self):
        expected = {
            "contents": [
                {"path": os.path.join(cwd(), "testing123", "test_non_model.txt"), "size": 12}
            ],
            "page": 1,
            "path": os.path.join(cwd(), "testing123"),
        }
        with temp_local_dir("testing123") as d:
            with temp_local_file(os.path.join(d, "test_non_model.txt"), "this is text") as test_file:
                req_path = os.path.join(os.getcwd(), d)
                self.call_and_expect_body("get", f"?path={req_path}", expected)

    def test_get_missing(self):
        self.call_and_expect_error("get", f"?path=nonexistent", HTTPExceptions.NO_CONTENT)

    def test_get_non_dir(self):
        with temp_local_file(f"some.txt", "this is text") as test_file:
            self.call_and_expect_error("get", f"?path={test_file}", HTTPExceptions.BAD_REQUEST)

class GithubImportTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(github_import)

    def test_path_required(self):
        with patch("fileserver.api.views.github_view.import_repo", return_value=None) as import_repo_mock:
            with temp_local_dir("testing123") as d:
                self.call_and_expect_error("post", f"?url=/", HTTPExceptions.BAD_REQUEST)

            import_repo_mock.assert_not_called()


    def test_url_required(self):
        with patch("fileserver.api.views.github_view.import_repo", return_value=None) as import_repo_mock:
            with temp_local_dir("testing123") as d:
                self.call_and_expect_error("post", f"?path={d}", HTTPExceptions.BAD_REQUEST)

            import_repo_mock.assert_not_called()

    def test_simple_case(self):
        with patch("fileserver.api.views.github_view.import_repo", return_value=None) as import_repo_mock:
            with temp_local_dir("testing123") as d:
                expected = {"path": d}
                response = self.call_and_expect_body("post", f"?path={d}&url=http://noop", expected)

                import_repo_mock.assert_called_once_with(d, "http://noop", overwrite=False)



class GithubExportTestCase(TestCaseBase):
    VIEW_CLASS = MethodViewWrapper(github_export)

    SIMPLE_BODY = {
            "github_token": "gh_token",
            "model_path": "the_model_path",
            "repo_name": "the_repo_name",
            "file_list": [],
            "data_path": "some/path",
            "commit_message": "first commit",
            }

    def test_simple(self):
        with patch("fileserver.api.views.github_view.connect_to_repo", return_value=Mock()),\
             patch("fileserver.api.views.github_view.export_repo_basic", return_value="2341234"),\
             temp_local_dir("testing123") as d:

            response = self.call_and_expect_code("post", f"?path={d}", 200, body=GithubExportTestCase.SIMPLE_BODY)
            self.assertEqual(response.content, b'{"sha": "2341234"}')
