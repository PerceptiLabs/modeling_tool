from django_http_exceptions import HTTPExceptions
from rest_framework.views import APIView
from fileserver.api.views.util import (
        get_path_param,
        make_path_response,
        )
import os

class FileView(APIView):
    def get(self, request, format=None):
        full_path, sub_path = get_path_param(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT
        return make_path_response(full_path, sub_path)

