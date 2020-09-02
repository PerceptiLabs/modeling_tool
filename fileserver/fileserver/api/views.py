from django.http import HttpResponse
from django.shortcuts import render
from django_http_exceptions import HTTPExceptions
from fileserver.settings import SERVING_ROOT
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from shutil import rmtree
import json
import os


def get_required_param(request, param):
    qp = request.query_params
    if not qp.__contains__(param):
        raise HTTPExceptions.BAD_REQUEST.with_content(f"Missing {param} parameter")
    return qp[param]


# Extracts the required "path" parameter from the request and validates it
def get_path_param(request):
    sub_path = get_required_param(request, "path")
    full_path = f"{SERVING_ROOT}/{sub_path}"
    if not os.path.abspath(full_path).startswith(SERVING_ROOT):
        msg = f"path parameter {sub_path} is not a valid path"
        raise HTTPExceptions.BAD_REQUEST().with_content(msg)
    return (full_path, sub_path)


def make_path_response(full_path, sub_path):
    response_body = {"path": sub_path}
    response_json = json.dumps(response_body)
    return HttpResponse(response_json, content_type="application/json")


class FileView(APIView):
    def get(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path, sub_path)


class JsonModelView(APIView):
    @staticmethod
    def load_json(full_path):
        with open(full_path, "r") as f:
            odne = False
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                raise HTTPExceptions.NO_CONTENT

    def get(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT

        response_body = {
            "path": sub_path,
            "model_body": JsonModelView.load_json(full_path),
        }
        response_json = json.dumps(response_body)
        return HttpResponse(response_json, content_type="application/json")

    @staticmethod
    def request_as_dict(request):
        # we can't decode the body as utf-8 json then it's a bad request
        try:
            as_utf8 = request.body.decode("utf-8")
            return json.loads(as_utf8)
        except:
            raise HTTPExceptions.BAD_REQUEST.with_content("Invalid json request")

    def post(self, request, format=None):
        full_path, sub_path = get_path_param(request)

        model_dict = JsonModelView.request_as_dict(request)

        with open(full_path, "w") as f:
            json.dump(model_dict, f)

        return make_path_response(full_path, sub_path)


class DirectoryView(APIView):
    def get(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path, sub_path)

    def post(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        os.makedirs(full_path, exist_ok=True)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path, sub_path)

    def delete(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        rmtree(full_path, ignore_errors=True)
        return make_path_response(full_path, sub_path)
