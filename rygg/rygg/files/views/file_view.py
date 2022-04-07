from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.response import Response
import itertools
import os

from rygg.files.paths import PathNotAvailable
from rygg.files.utils.file_choosing import open_file_dialog, open_saveas_dialog
from rygg.files.utils.file import get_text_lines
from rygg.files.views.util import (
    get_path_param,
    get_optional_param,
    json_response,
    make_path_response,
)
from rygg.settings import IS_CONTAINERIZED
import rygg.files.views.util


def full_path(request):
    try:
        # using the full name to allow for easy mocking
        ret = rygg.files.views.util.get_path_param(request)
        if not os.path.isfile(ret):
            raise HTTPExceptions.NOT_FOUND
        return ret
    except PathNotAvailable as e:
        raise HTTPExceptions.NOT_FOUND.with_content(e)


class FileView(RetrieveDestroyAPIView):
    def get(self, request, format=None):
        if IS_CONTAINERIZED:
            raise HTTPExceptions.BAD_REQUEST.with_content(
                "not supported in docker installations"
            )
        path = full_path(request)
        return make_path_response(path)

    def delete(self, request, format=None):
        if IS_CONTAINERIZED:
            raise HTTPExceptions.BAD_REQUEST.with_content(
                "not supported in docker installations"
            )
        path = full_path(request)
        os.remove(path)
        return make_path_response(path)


import json


def get_file_types_from_request(request):
    as_json = get_optional_param(request, "file_types", None)
    if not as_json:
        return

    as_list = json.loads(as_json)

    for d in as_list:
        name = d.get("name")
        if not name:
            raise HTTPExceptions.BAD_REQUEST.with_content(
                f"Missing name in file_types record: {d}"
            )

        extensions = d.get("extensions")
        if extensions is None:
            raise HTTPExceptions.BAD_REQUEST.with_content(
                f"Missing extensions in file_types record: {d}"
            )

        extensions_as_str = " ".join(d["extensions"])
        yield (name, extensions_as_str)


@api_view(["GET"])
def pick_file(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.NOT_FOUND.with_content(
            "pick file isn't available in server mode"
        )

    initial_dir = get_optional_param(request, "initial_dir", "~")
    file_types = get_file_types_from_request(request)
    title = get_optional_param(request, "title", None)

    try:
        path = open_file_dialog(
            initial_dir=initial_dir, file_types=file_types, title=title
        )
        return Response({"path": path})
    except Exception as e:
        raise HTTPExceptions.INTERNAL_SERVER_ERROR.with_content(e.args)


@api_view(["GET"])
def saveas_file(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.NOT_FOUND.with_content(
            "SaveAs file isn't available in server mode"
        )

    initial_dir = get_optional_param(request, "initial_dir", "~")
    file_types = get_file_types_from_request(request)
    title = get_optional_param(request, "title", None)

    try:
        path = open_saveas_dialog(
            initial_dir=initial_dir, file_types=file_types, title=title
        )
        return Response({"path": path})
    except Exception as e:
        raise HTTPExceptions.INTERNAL_SERVER_ERROR.with_content(e.args)
