from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rygg.api.models import Model, Dataset
from rygg.api.serializers import ModelSerializer, DatasetSerializer

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.available_objects.filter(project__is_removed=False).order_by("-model_id")
    serializer_class = ModelSerializer

    @action(methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], detail=True)
    def datasets(self, request, pk):
        ds = Model.available_objects.get(pk=pk, project__is_removed=False)
        if not ds:
            raise HTTPExceptions.NOT_FOUND
        ds_datasets = ds.datasets

        if request.method == "GET":
            datasets = Dataset.available_objects.filter(models=pk)
            serializer = DatasetSerializer(datasets, many=True)
            return Response(serializer.data)
        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_datasets = Dataset.available_objects.filter(dataset_id__in=ids)
            ds_datasets.add(*new_datasets)

            serializer = DatasetSerializer(ds.datasets, many=True)
            return Response(serializer.data)
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(',')

            datasets_to_remove = Dataset.available_objects.filter(dataset_id__in=ids)
            ds_datasets.remove(*datasets_to_remove)

            serializer = DatasetSerializer(ds.datasets, many=True)
            return Response(serializer.data)

        else:
            raise HTTPExceptions.METHOD_NOT_ALLOWED.withContent(request.method)

