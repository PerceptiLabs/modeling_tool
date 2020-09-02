from contextlib import contextmanager
from django.test import TestCase
from django_http_exceptions import HTTPExceptions
from fileserver.api.views import FileView, DirectoryView, JsonModelView
from rest_framework.test import APIRequestFactory, APIClient
import json
import os


@contextmanager
def local_file_cleanup(name):
    try:
        yield name
    finally:
        if os.path.isfile(name):
            os.remove(name)


@contextmanager
def temp_local_file(name, content):
    with open(name, "w") as f:
        f.write(content)

    with local_file_cleanup(name) as f:
        yield f


@contextmanager
def temp_local_dir(name):
    os.mkdir(name)
    try:
        yield name
    finally:
        if os.path.exists(name):
            os.rmdir(name)


@contextmanager
def temp_json_file(name, content: dict):
    as_json = json.dumps(content)
    with temp_local_file(name, as_json) as f:
        yield f


class SettingsTest(TestCase):
    EXPECTED_HOSTS = set(["127.0.0.1", "localhost"])

    def test_allowed_hosts(self):
        from fileserver.settings import ALLOWED_HOSTS

        l = set(ALLOWED_HOSTS)
        self.assertSetEqual(l, self.EXPECTED_HOSTS)


class TestCaseBase(TestCase):
    def build_call(self, method_name, path, body=None):
        self.factory = APIRequestFactory()
        method = getattr(self.factory, method_name)
        request = method(path, body, format="json") if body else method(path)
        view = self.VIEW_CLASS.as_view()

        def do_call():
            return view(request)

        return do_call

    def call_and_expect_code(self, method_name, path, code, body=None):
        call = self.build_call(method_name, path, body=body)
        response = call()
        self.assertEqual(response.status_code, code)
        return response

    def call_and_expect_error(self, method_name, path, error_class):
        call = self.build_call(method_name, path)
        self.assertRaises(error_class, call)


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


class DirectoriesViewTestCase(TestCaseBase):
    VIEW_CLASS = DirectoryView

    def test_get_directories(self):
        with temp_local_dir("testing123") as d:
            self.call_and_expect_code("get", f"/directories?path={d}", 200)

    def test_head_directories(self):
        with temp_local_dir("testing123") as d:
            self.call_and_expect_code("head", f"/directories?path={d}", 200)

    def test_get_directories_with_breakout_path(self):
        self.call_and_expect_error(
            "get", f"/directories?path=fileserver/../..", HTTPExceptions.BAD_REQUEST
        )

    def test_post_directories(self):
        # test the post
        self.call_and_expect_code(
            "post", f"/directories?path=fileserver/testing123", 200
        )
        assert os.path.isdir(
            "fileserver/testing123"
        ), f"expected post /directories to create file testing123"

        try:
            os.removedirs("fileserver/testing123")
        except:
            pass

    def test_delete_directories(self):
        with temp_local_dir("to_delete") as d:
            self.assertTrue(os.path.isdir(d), "the directory wasn't set up")
            self.call_and_expect_code("delete", f"/directories?path={d}", 200)
            self.assertFalse(os.path.isdir(d), "the directory wasn't set up")


class JsonModelsViewTestCase(TestCaseBase):
    VIEW_CLASS = JsonModelView

    def test_get_json_models(self):
        with temp_json_file(
            "test_model.json", {"this": "is json", "and this is a number": 123}
        ) as test_file:
            resp = self.call_and_expect_code(
                "get", f"/json_models?path={test_file}", 200
            )
            as_dict = json.loads(resp.content)
            if as_dict["path"] != test_file:
                raise exception(
                    f"get /json_models didn't populate the path in the response body"
                )
            if as_dict["model_body"]["this"] != "is json":
                raise exception(
                    f"get /json_models didn't populate the json body correctly"
                )

    def test_get_json_models_with_non_json(self):
        with temp_local_file("test_non_model.txt", "this is text") as test_file:
            self.call_and_expect_error(
                "get", f"/json_models?path={test_file}", HTTPExceptions.NO_CONTENT
            )

    def test_post_json_models(self):
        req = {"this": "is json"}
        with local_file_cleanup("testing123.json") as f:
            self.call_and_expect_code("post", f"/json_models?path={f}", 200, body=req)
            self.assertTrue(
                os.path.exists(f), f"expected post /json_models to create the file {f}"
            )

    def test_post_json_models_with_non_json(self):
        with local_file_cleanup("testing123.json") as f:
            cur_url = f"/json_models?path={f}"
            self.call_and_expect_error("post", cur_url, HTTPExceptions.BAD_REQUEST)
            self.assertFalse(
                os.path.exists(f),
                f"expected post /json_models to not create an invalid json file",
            )
