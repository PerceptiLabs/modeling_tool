from django.test import TestCase
from rest_framework.test import APIRequestFactory
import json

from rygg.api.models import Project


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
        self.maxDiff = None
        self.assertDictEqual(as_dict, expected_body)
        return response

    def call_and_expect_error(self, method_name, path, error_class, body=None):
        call = self.build_call(method_name, path, body=body)
        self.assertRaises(error_class, call)
