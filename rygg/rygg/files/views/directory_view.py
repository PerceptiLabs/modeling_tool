from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shutil import rmtree
import os

from rygg.files.utils.file_choosing import open_directory_dialog
import rygg.files.views.util
from rygg.files.views.util import (
        get_optional_param,
        make_path_response,
        json_response,
        )
from rygg.settings import IS_CONTAINERIZED

def request_path(request):
    return rygg.files.views.util.get_path_param(request)


class DirectoryView(APIView):

    def get(self, request):
        full_path = request_path(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path)


    def post(self, request):
        if IS_CONTAINERIZED:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY

        full_path = request_path(request)
        os.makedirs(full_path, exist_ok=True)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path)


    def delete(self, request):
        full_path = request_path(request)
        if not os.path.isdir(full_path):
            raise HTTPExceptions.NO_CONTENT
        rmtree(full_path, ignore_errors=True)
        return make_path_response(full_path)


@api_view(["GET"])
def get_resolved_dir(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.BAD_REQUEST.with_content("get_resolved_dir isn't supported in docker installations")

    resolved = request_path(request)
    return make_path_response(resolved)


@api_view(["GET"])
def pick_directory(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.NOT_FOUND.with_content("pick directory isn't available in server mode")

    initial_dir = get_optional_param(request, "initial_dir", "~")
    title = get_optional_param(request, "title", None)


    try:
        path = open_directory_dialog(initial_dir=initial_dir, title=title)
        return Response({"path": path})
    except Exception as e:
        raise HTTPExceptions.INTERNAL_SERVER_ERROR.with_content(e.args)
