from django_http_exceptions import HTTPExceptions
from fileserver.api.views.util import (
        get_path_param,
        make_path_response,
        )
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from shutil import rmtree
import os

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
