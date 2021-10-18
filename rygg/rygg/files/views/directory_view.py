from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shutil import rmtree
import os

from rygg.files.models.directory import (
        get_folder_content as get_folder_content_model,
        get_tutorial_data as get_tutorial_data_model,
        get_drives as get_drives_model,
        resolve_dir as resolve_dir_model,
        get_root_path as get_root_path_model,
        )
from rygg.files.utils.file_choosing import open_directory_dialog
from rygg.files.views.util import (
        get_path_param,
        get_required_param,
        get_optional_param,
        make_path_response,
        json_response,
        )
from rygg.settings import IS_CONTAINERIZED

class DirectoryView(APIView):
    def get(self, request):
        full_path = get_path_param(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
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

@api_view(["GET", "HEAD"])
def get_drives(request):
    ret = get_drives_model()
    if ret:
        response = {"drives": ret}
        return json_response(response)

    raise HTTPExceptions.NO_CONTENT


@api_view(["GET"])
def get_folder_content(request):
    raw_path = get_required_param(request, "path")
    response = get_folder_content_model(raw_path)
    return json_response(response)

@api_view(["GET"])
def get_resolved_dir(request):
    # get_path_param always resolves the dir
    raw_path = get_required_param(request, "path")
    resolved = resolve_dir_model(raw_path)
    return make_path_response(resolved)

@api_view(["GET", "HEAD"])
def get_root_path(request):
    ret = get_root_path_model()
    if ret:
        return make_path_response(ret)

    raise HTTPExceptions.NO_CONTENT

@api_view(["GET"])
def pick_directory(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.NOT_FOUND.with_content("pick directory isn't available in server mode")

    initial_dir = get_optional_param(request, "initial_dir", "~")
    title = get_optional_param(request, "title", None)


    path = open_directory_dialog(initial_dir=initial_dir, title=title)
    return Response({"path": path})

