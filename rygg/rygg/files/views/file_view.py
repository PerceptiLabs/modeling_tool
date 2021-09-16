from django_http_exceptions import HTTPExceptions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rygg.files.views.util import (
        get_path_param,
        get_required_param,
        make_path_response,
        make_file_content_response
        )
import os

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
