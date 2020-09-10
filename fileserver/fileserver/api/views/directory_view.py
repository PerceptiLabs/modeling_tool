from django_http_exceptions import HTTPExceptions
from fileserver.api.views.util import (
        get_path_param,
        get_optional_param,
        make_path_response,
        json_response,
        )
from fileserver.api.models.directory import (
        get_folder_content,
        get_tutorial_data as get_tutorial_data_model,
        )
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from shutil import rmtree
import os

class DirectoryView(APIView):
    def get(self, request):
        full_path = get_path_param(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        include_content = bool(get_optional_param(request, "include_content", "false"))
        if include_content:
            response = get_folder_content(full_path)
            return json_response(response)
        else:
            return make_path_response(full_path)

    def post(self, request):
        full_path = get_path_param(request)
        os.makedirs(full_path, exist_ok=True)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path)

    def delete(self, request):
        full_path = get_path_param(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        rmtree(full_path, ignore_errors=True)
        return make_path_response(full_path)

@api_view(["GET", "HEAD"])
def get_tutorial_data(request):
    ret = get_tutorial_data_model()
    if ret:
        return make_path_response(ret)

    raise HTTPExceptions.NO_CONTENT
