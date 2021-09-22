from django.conf import settings
from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
import urllib

from rygg.api.models import Dataset, Model
from rygg.api.serializers import DatasetSerializer, ModelSerializer
from rygg.files.tasks import download_async
from rygg.files.views.util import request_as_dict, get_required_param


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.available_objects.filter(project__is_removed=False).order_by("-dataset_id")
    serializer_class = DatasetSerializer

    @action(methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], detail=True)
    def models(self, request, pk):
        ds = Dataset.available_objects.get(pk=pk, project__is_removed=False)
        if not ds:
            raise HTTPExceptions.NOT_FOUND
        ds_models = ds.models

        if request.method == "GET":
            models = Model.available_objects.filter(datasets=pk)

        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_models = Model.available_objects.filter(model_id__in=ids)
            ds_models.add(*new_models)
            models = ds.models
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(',')

            models_to_remove = Model.available_objects.filter(model_id__in=ids)
            ds_models.remove(*models_to_remove)
            models = ds.models

        else:
            raise HTTPExceptions.METHOD_NOT_ALLOWED.withContent(request.method)

        serializer = ModelSerializer(models, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def list_remote(self, request):
        res = urllib.request.urlopen(settings.DATA_LIST)
        lines = [l.decode('utf-8') for l in res.readlines()]
        cr = csv.reader(lines)

        # name, size, category, description
        #TODO: add description and other columns in file and here
        rows = [[row[0], row[2], row[3]] for row in cr]

        return Response(rows, 201)


    @action(detail=False, methods=['POST'])
    def create_from_remote(self, request):
        d = request_as_dict(request)
        name = get_required_param(request, "id")
        dest_path = get_required_param(request, "destination")
        data_url = f"{settings.DATA_BLOB}/{name}"
        task_id = download_async(data_url, dest_path)
        return Response({"task_id": task_id}, 201)

