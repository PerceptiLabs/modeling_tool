from django.conf import settings
from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import csv
import urllib
import urllib.request

from rygg.api.models import Dataset, Model
from rygg.api.serializers import DatasetSerializer, ModelSerializer
from rygg.files.tasks import download_async
from rygg.files.views.util import request_as_dict, get_required_param, get_optional_param

def lines_from_url(url):
    with urllib.request.urlopen(url) as res:
        for l in res.readlines():
            yield l.decode('utf-8')

def csv_lines_to_dict(lines):
    reader = csv.reader(lines)
    first = None
    for row in reader:
        if first is None:
            first = row
        else:
            yield dict(zip(first, row))

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

    def fetch_remote_categories(self):
        lines = lines_from_url(settings.DATA_CATEGORY_LIST)
        entries = list(csv_lines_to_dict(lines))
        return {d["name"]: d for d in entries}


    @action(detail=False, methods=['GET'])
    def remote_categories(self, request):
        return Response(self.fetch_remote_categories(), 201)

    @action(detail=False, methods=['GET'])
    def remote_with_categories(self, request):
        lines = lines_from_url(settings.DATA_LIST)
        remote_datasets = list(csv_lines_to_dict(lines))

        # Make a table of datasets that have been downloaded from our remote
        # Sort the query by dataset_id so that the newest ones end up being the representatives in the lists
        datasets_from_remote_query = Dataset.objects.filter(source_url__startswith = settings.DATA_BLOB).order_by('dataset_id')
        prefix_len = len(settings.DATA_BLOB) + 1 # +1 for the slash "/"
        datasets_from_remote = {d.source_url[prefix_len:] : d.dataset_id for d in datasets_from_remote_query}

        # update the response with the newest dataset's id, if any
        for dataset in remote_datasets:
            id = datasets_from_remote.get(dataset['UniqueName'])
            if id:
                dataset["localDatasetID"] = id

        response = {
            "categories": self.fetch_remote_categories(),
            "datasets": remote_datasets,
        }
        return Response(response, 201)

    @action(detail=False, methods=['GET'])
    def remote(self, request):
        lines = lines_from_url(settings.DATA_LIST)
        entries = list(csv_lines_to_dict(lines))
        return Response(entries, 201)


    @action(detail=False, methods=['POST'])
    def create_from_remote(self, request):
        ds_name = get_optional_param(request, "name", f"New Dataset")
        remote_name = get_required_param(request, "id")
        data_url = f"{settings.DATA_BLOB}/{remote_name}"
        project_id = get_required_param(request, "project_id")
        dest_path = get_required_param(request, "destination")

        dataset = Dataset(project_id=project_id, name=ds_name, source_url=data_url, location=dest_path)
        dataset.save()

        task_id = download_async(dataset.dataset_id)
        response = {
            "task_id": task_id,
            "dataset_id": dataset.dataset_id,
        }
        return Response(response, 201)

