from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound
from django_http_exceptions import HTTPExceptions
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rygg import __version__
from rygg.api.app import updates_available
from rygg.api.models import Project, Model, Notebook, Dataset
from rygg.api.serializers import ProjectSerializer, ModelSerializer, NotebookSerializer, DatasetSerializer
from rygg.api.services import GitHubService
import json

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.available_objects.filter(is_removed=False).order_by("-project_id")
    serializer_class = ProjectSerializer


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
            return HttpResponse(json.dumps(serializer.data))
        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_datasets = Dataset.available_objects.filter(dataset_id__in=ids)
            ds_datasets.add(*new_datasets)

            serializer = DatasetSerializer(ds.datasets, many=True)
            return HttpResponse(json.dumps(serializer.data))
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(',')

            datasets_to_remove = Dataset.available_objects.filter(dataset_id__in=ids)
            ds_datasets.remove(*datasets_to_remove)

            serializer = DatasetSerializer(ds.datasets, many=True)
            return HttpResponse(json.dumps(serializer.data))

        else:
            raise HTTPExceptions.METHOD_NOT_ALLOWED.withContent(request.method)

class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.available_objects.filter(project__is_removed=False).order_by("-notebook_id")
    serializer_class = NotebookSerializer


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
            serializer = ModelSerializer(models, many=True)
            return HttpResponse(json.dumps(serializer.data))
        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_models = Model.available_objects.filter(model_id__in=ids)
            ds_models.add(*new_models)

            serializer = ModelSerializer(ds.models, many=True)
            return HttpResponse(json.dumps(serializer.data))
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(',')

            models_to_remove = Model.available_objects.filter(model_id__in=ids)
            ds_models.remove(*models_to_remove)

            serializer = ModelSerializer(ds.models, many=True)
            return HttpResponse(json.dumps(serializer.data))

        else:
            raise HTTPExceptions.METHOD_NOT_ALLOWED.withContent(request.method)


class IssuesViewSet(viewsets.ViewSet):
    def create(self, request):
        requestPayload = json.loads(request.body.decode("utf-8"))
        githubService = GitHubService(settings);

        try:
            result = githubService.createIssue(**requestPayload)
            return HttpResponse(result.text, content_type='application/json')
        except:
            return HttpResponseServerError()


@api_view(['GET'])
def get_version(request):
    json_str = json.dumps({"version": __version__})
    return HttpResponse(json_str, content_type="application/json")


@api_view(['GET'])
def get_updates_available(request):
    json_str = json.dumps({"newer_versions": updates_available()})
    return HttpResponse(json_str, content_type="application/json")

@api_view(["GET"])
def is_enterprise(request):
    json_str = json.dumps({"is_enterprise": settings.IS_CONTAINERIZED})
    return HttpResponse(json_str, content_type="application/json")

from rygg.celery import app as celery_app
from celery.result import AsyncResult

class TaskViewSet(viewsets.GenericViewSet):
    def retrieve(self, request, pk=None):
        task = AsyncResult(pk, app=celery_app)
        if not task.info:
            return HttpResponseNotFound()

        return Response({"state": task.state, **task.info})

    def destroy(self, request, pk=None):
        task = AsyncResult(pk, app=celery_app)
        if not task.info:
            return HttpResponseNotFound()

        celery_app.control.terminate(pk)
        return Response()
