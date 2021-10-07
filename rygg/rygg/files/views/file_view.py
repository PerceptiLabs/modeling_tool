from django_http_exceptions import HTTPExceptions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rygg.files.views.util import (
    get_path_param,
    get_required_param,
    get_optional_param,
    make_path_response,
    make_file_content_response
)
from rygg.files.utils.file_choosing import open_file_dialog
import os
from rygg.settings import IS_CONTAINERIZED

class FileView(APIView):
    def get(self, request, format=None):
        full_path = get_path_param(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path)

    def delete(self, request, format=None):
        full_path = get_path_param(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT
        os.remove(full_path)
        return make_path_response(full_path)

@api_view(["GET"])
def get_file_content(request):
    full_path = get_required_param(request, "path")

    if not os.path.isfile(full_path):
        raise HTTPExceptions.NO_CONTENT

    results = make_file_content_response(request, full_path)

    if results:
        return results

    raise HTTPExceptions.NO_CONTENT

import json
def get_file_types_from_request(request):
    as_json = get_optional_param(request, "file_types", None)
    if not as_json:
        return

    as_list = json.loads(as_json)

    for d in as_list:
        name = d.get("name")
        if not name:
            raise HTTPExceptions.BAD_REQUEST.with_content(f"Missing name in file_types record: {d}")

        extensions = d.get("extensions")
        if extensions is None:
            raise HTTPExceptions.BAD_REQUEST.with_content(f"Missing extensions in file_types record: {d}")

        extensions_as_str = " ".join(d["extensions"])
        yield (name, extensions_as_str)

@api_view(["GET"])
def pick_file(request):
    if IS_CONTAINERIZED:
        raise HTTPExceptions.NOT_FOUND.with_content("pick file isn't available in server mode")

    initial_dir = get_optional_param(request, "initial_dir", "~")
    file_types = get_file_types_from_request(request)
    title = get_optional_param(request, "title", None)


    path = open_file_dialog(initial_dir=initial_dir, file_types=file_types, title=title)
    return Response({"path": path})

