from datetime import datetime
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django_http_exceptions import HTTPExceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer, FileField, CharField, BooleanField
from rest_framework.views import APIView
import json
import os
import shutil
import time

from rygg.api.models import Dataset, Project
from rygg.files.exceptions import UserError
from rygg.files.tasks import unzip_async
from rygg.files.views.util import json_response, get_project_id_from_request, get_required_param
from rygg.settings import file_upload_dir, is_upload_allowed
import rygg.settings

class UploadSerializer(Serializer):
    file_uploaded = FileField()
    dest_file = CharField()
    overwrite = BooleanField(default=False)

    class Meta:
        fields = ['file_uploaded', 'dest_file', 'overwrite']

def iso_from_utc_timestamp(ts):
    return datetime.utcfromtimestamp(ts).isoformat()

def _get_file_info(filename):
    stat = os.stat(filename)
    return {
        'name': os.path.basename(filename),
        'size': stat.st_size,
        'created': iso_from_utc_timestamp(stat.st_ctime),
        'modified': iso_from_utc_timestamp(stat.st_mtime),
    }


@api_view(["GET"])
def get_upload_dir(request):
    project_id = get_project_id_from_request(request)
    project = Project.available_objects.get(pk=project_id)
    return json_response({"path": project.base_directory})

class UploadView(APIView):
    serializer_class = UploadSerializer


    def get(self, request):
        if not is_upload_allowed():
            return HttpResponseNotFound("This server isn't configured to allow uploads")

        filename = get_required_param(request, "filename")
        project_id = get_project_id_from_request(request)
        project = Project.available_objects.get(pk=project_id)

        file_path = os.path.join(project.base_directory, filename)
        try:
            response = _get_file_info(file_path)
            return Response(response)
        except FileNotFoundError:
            raise HTTPExceptions.NOT_FOUND(f"{file_path} doesn't exist")

    def post(self, request):
        if not is_upload_allowed():
            return HttpResponseNotFound("This server isn't configured to allow uploads")

        project_id = get_project_id_from_request(request)
        project = Project.available_objects.get(pk=project_id)

        file_uploaded = request.FILES.get('file_uploaded')
        if not file_uploaded:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("A file wasn't uploaded")

        dest_file_name = file_uploaded.name
        if not dest_file_name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("A file name wasn't provided.")

        if dest_file_name == "file_uploaded":
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("Internal error")

        dataset_id = request.POST.get('dataset_id')
        dataset = dataset_id and Dataset.available_objects.get(pk=dataset_id)

        if dataset_id and not dataset:
            raise HTTPExceptions.NOT_FOUND(f"Dataset {dataset_id} not found")

        if dataset and dataset.location != dest_file_name:
            raise HTTPExceptions.BAD_REQUEST.with_content(f"file upload for dataset {dataset_id} must match dataset location.")

        overwrite = request.POST.get('overwrite') in ['true', 'True', 1]

        dest_file = os.path.join(project.base_directory, dest_file_name)
        if os.path.exists(dest_file) and not bool(overwrite):
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(f"File {dest_file_name} exists and overwrite is false")

        shutil.move(file_uploaded.temporary_file_path(), dest_file)

        if dataset:
            dataset.status = "uploaded"
            dataset.save()

        # we just moved a file out from under the temp file. Now touch the original location so it has something to delete and doesn't throw spurious errors
        open(file_uploaded.temporary_file_path(), "wb").close()

        content_type = file_uploaded.content_type

        if (open(dest_file, "rb").read(4) == b'PK\x03\x04'):
            task_id = unzip_async(dest_file)
            return Response({"task_id": task_id})

        response = _get_file_info(dest_file)
        return Response(response, 201)

