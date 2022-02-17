from rest_framework.decorators import api_view

from rygg.api.models import Dataset, Project
from rygg.files.views.util import json_response, get_project_from_request

@api_view(["GET"])
def get_upload_dir(request):
    project = get_project_from_request(request)
    return json_response({"path": project.base_directory})
