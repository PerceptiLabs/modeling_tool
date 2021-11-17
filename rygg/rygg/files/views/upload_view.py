from rest_framework.decorators import api_view

from rygg.api.models import Dataset, Project
from rygg.files.views.util import json_response, get_project_id_from_request

@api_view(["GET"])
def get_upload_dir(request):
    project_id = get_project_id_from_request(request)
    project = Project.available_objects.get(pk=project_id)
    return json_response({"path": project.base_directory})
