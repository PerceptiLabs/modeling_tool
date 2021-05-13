from datetime import datetime
from django.http import HttpResponseNotFound
from django_http_exceptions import HTTPExceptions
from fileserver import settings
from fileserver.api.exceptions import UserError
from rest_framework.response import Response
from rest_framework.serializers import Serializer, FileField, CharField, BooleanField
from rest_framework.views import APIView
import json
import os, shutil

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

class UploadView(APIView):
    serializer_class = UploadSerializer


    def get(self, request):
        if not settings.FILE_UPLOAD_DIR:
            return HttpResponseNotFound("This server isn't configured to allow uploads")

        filename = request.GET.get("filename")
        if not filename:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("Parameter 'filename' is required")

        file_path = os.path.join(settings.FILE_UPLOAD_DIR, filename)
        try:
            response = _get_file_info(file_path)
            return Response(response)
        except FileNotFoundError:
            raise HTTPExceptions.NOT_FOUND(f"{file_path} doesn't exist")

    def post(self, request):
        if not settings.FILE_UPLOAD_DIR:
            return HttpResponseNotFound("This server isn't configured to allow uploads")

        print(request.FILES)
        file_uploaded = request.FILES.get('file_uploaded')
        if not file_uploaded:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("A file wasn't uploaded")

        dest_file_name = file_uploaded.name
        if not dest_file_name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("A file name wasn't provided.")

        if dest_file_name == "file_uploaded":
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content("Internal error")

        overwrite = request.POST.get('overwrite') in ['true', 'True', 1]

        dest_file = os.path.join(settings.FILE_UPLOAD_DIR, dest_file_name)
        if os.path.exists(dest_file) and not bool(overwrite):
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(f"File {dest_file_name} exists and overwrite is false")

        shutil.move(file_uploaded.temporary_file_path(), dest_file)

        # we just moved a file out from under the temp file. Now touch the original location so it has something to delete and doesn't throw spurious errors
        open(file_uploaded.temporary_file_path(), "wb").close()

        content_type = file_uploaded.content_type
        response = _get_file_info(dest_file)
        return Response(response, 201)

