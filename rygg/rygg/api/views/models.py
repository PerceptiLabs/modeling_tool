from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import json
import os

from rygg.api.models import Model, Dataset
from rygg.api.serializers import ModelSerializer, DatasetSerializer
from rygg.files.views.util import (
    get_project_from_request,
    get_required_param,
    json_response,
    make_path_response,
    protect_read_only_enterprise_field,
    request_as_dict,
)


class ModelViewSet(viewsets.ModelViewSet):
    serializer_class = ModelSerializer

    def get_queryset(self):
        return Model.get_queryset(self.request.user).order_by("-model_id")

    def create(self, request):
        protect_read_only_enterprise_field(request, "location")
        return super().create(request)

    def update(self, request, **kwargs):
        protect_read_only_enterprise_field(request, "location")
        return super().update(request, **kwargs)

    @action(methods=["GET"], detail=True)
    def get_json(self, request, pk):
        model = Model.get_queryset(request.user).get(pk=pk)
        content = model.content
        if content == None:
            raise HTTPExceptions.NOT_FOUND.with_content("No valid json found")
        response_body = {"model_body": content}
        return json_response(response_body)

    @action(methods=["POST", "PATCH", "PUT"], detail=True)
    def save_json(self, request, pk):
        model_dict = request_as_dict(request)

        model = Model.get_queryset(request.user).get(pk=pk)
        try:
            model.save_content(model_dict)
        except PermissionError as e:
            raise HTTPExceptions.BAD_REQUEST.with_content(f"Permission error: {e}")

        return Response(None, 201)

    @action(methods=["GET", "POST", "PATCH", "PUT", "DELETE"], detail=True)
    def datasets(self, request, pk):
        instance = Model.get_queryset(request.user).get(pk=pk)
        ds_datasets = instance.datasets

        if request.method == "GET":
            datasets = Dataset.get_queryset(request.user).filter(models=pk)
            serializer = DatasetSerializer(datasets, many=True)
            return Response(serializer.data)
        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_datasets = Dataset.get_queryset(request.user).filter(dataset_id__in=ids)
            ds_datasets.add(*new_datasets)

            serializer = DatasetSerializer(ds_datasets, many=True)
            return Response(serializer.data)
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(",")

            datasets_to_remove = Dataset.get_queryset(request.user).filter(
                dataset_id__in=ids
            )
            ds_datasets.remove(*datasets_to_remove)

            serializer = DatasetSerializer(ds_datasets, many=True)
            return Response(serializer.data)
        else:

            raise HTTPExceptions.METHOD_NOT_ALLOWED.withContent(request.method)

    @action(methods=["GET"], detail=False)
    def next_name(self, request):
        prefix = get_required_param(request, "prefix")
        project_id = get_project_from_request(request).project_id
        ret = Model.next_name(project_id, prefix, request.user)
        return Response({"next_name": ret}, 200)
