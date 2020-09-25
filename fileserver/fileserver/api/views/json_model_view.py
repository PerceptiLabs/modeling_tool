from rest_framework.views import APIView
from fileserver.api.views.util import (
        get_path_param,
        request_as_dict,
        make_path_response,
        json_response,
        )
import json
import os
from django_http_exceptions import HTTPExceptions

class JsonModelView(APIView):
    def model_path(self, request):
        requested_path = get_path_param(request)
        if requested_path.lower().endswith(".json"):
            return requested_path
        else:
            return os.path.join(requested_path, "model.json")

    @staticmethod
    def load_json(full_path):
        with open(full_path, "r") as f:
            odne = False
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                raise HTTPExceptions.NO_CONTENT

    def get(self, request, format=None):
        full_path = self.model_path(request)
        if not os.path.isfile(full_path):
            raise HTTPExceptions.NO_CONTENT

        response_body = {
            "path": full_path,
            "model_body": JsonModelView.load_json(full_path),
        }
        return json_response(response_body)

    def post(self, request, format=None):
        full_path = self.model_path(request)

        model_dict = request_as_dict(request)

        model_dir = os.path.dirname(full_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)

        if not os.path.isdir(model_dir):
            raise HTTPExceptions.BAD_REQUEST.with_content(f"not a directory: {model_dir}")

        with open(full_path, "w") as f:
            json.dump(model_dict, f)

        return make_path_response(full_path)


