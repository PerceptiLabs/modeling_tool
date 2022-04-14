import csv
import itertools
import urllib
import urllib.request
from contextlib import contextmanager

from django.conf import settings
from django.core.exceptions import ValidationError
from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import rygg.files.views.util
from rygg.api.models import Dataset, Model
from rygg.api.serializers import DatasetSerializer, ModelSerializer
from rygg.files.views.util import (
    get_optional_int_param,
    get_optional_param,
    get_project_from_post,
    get_project_from_request,
    get_required_choice_param,
    get_required_choice_post,
    get_required_param,
    json_response,
    protect_read_only_enterprise_field,
    request_as_dict,
)
from rygg.settings import IS_CONTAINERIZED, is_upload_allowed


def request_path(request):
    return rygg.files.views.util.get_path_param(request)


def lines_from_url(url):
    with urllib.request.urlopen(url) as res:
        for l in res.readlines():
            yield l.decode("utf-8")


def csv_lines_to_dict(lines):
    reader = csv.reader(lines)
    first = None
    for row in reader:
        if first is None:
            first = row
        else:
            yield dict(zip(first, row))


@contextmanager
def validation_conversion():
    try:
        yield
    except ValidationError as e:
        raise HTTPExceptions.BAD_REQUEST.with_content("\n".join(e.messages))


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer

    def get_queryset(self):
        user = self.request.user
        return Dataset.get_queryset(user).order_by("-dataset_id")

    def alias_project_id(self, request):
        # copy over project_id to project for backward compatibility
        if not "project" in request.data:
            if not "project_id" in request.data:
                raise HTTPExceptions.BAD_REQUEST()
            else:
                request.data["project"] = request.data["project_id"]

        request.data["project_id"] = request.data["project"]

    def create(self, request):
        # We don't support creating from a POST in enterprise
        # Callers will use create_from_remote and create_from_upload instead
        if IS_CONTAINERIZED:
            raise HTTPExceptions.METHOD_NOT_ALLOWED

        self.alias_project_id(request)

        # Ensure that the project is available to the user
        get_project_from_post(request)
        return super().create(request)

    @action(detail=True, methods=["DELETE"])
    def delete(self, request, pk):
        ds = Dataset.get_by_id(pk)
        if not ds:
            raise HTTPExceptions.NOT_FOUND
        Dataset.unregister(dataset_id=pk)
        Dataset.delete_from_disk(dataset=ds)
        return Response(None, 204)

    @action(detail=True, methods=["DELETE"])
    def unregister(self, request, pk):
        ds = Dataset.get_by_id(pk)
        if not ds:
            raise HTTPExceptions.NOT_FOUND
        Dataset.unregister(dataset_id=pk)
        return Response(None, 204)

    def update(self, request, **kwargs):
        protect_read_only_enterprise_field(request, "location")
        return super().update(request, **kwargs)

    @action(methods=["GET", "POST", "PATCH", "PUT", "DELETE"], detail=True)
    def models(self, request, pk):
        ds = Dataset.get_by_id(pk)
        if not ds:
            raise HTTPExceptions.NOT_FOUND
        ds_models = ds.models

        if request.method == "GET":
            models = Model.get_queryset(request.user).filter(datasets=pk)

        elif request.method in ["PATCH", "POST", "PUT"]:
            ids = request.data.get("ids")

            if not ids:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            new_models = Model.get_queryset(request.user).filter(model_id__in=ids)
            ds_models.add(*new_models)
            models = ds.models
        elif request.method == "DELETE":
            ids_str = request.query_params.get("ids")
            if not ids_str:
                raise HTTPExceptions.BAD_REQUEST.with_content("ids field is required")

            ids = ids_str.split(",")

            models_to_remove = Model.get_queryset(request.user).filter(model_id__in=ids)
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

    @action(detail=False, methods=["GET"])
    def remote_categories(self, request):
        return Response(self.fetch_remote_categories(), 201)

    def fetch_remote_datasets_list(self):
        lines = lines_from_url(settings.DATA_LIST)
        remote_datasets = list(csv_lines_to_dict(lines))

        # Make a table of datasets that have been downloaded from our remote
        # Sort the query by dataset_id so that the newest ones end up being the representatives in the lists
        datasets_from_remote_query = (
            Dataset.get_queryset(self.request.user)
            .filter(source_url__startswith=settings.DATA_BLOB)
            .order_by("dataset_id")
        )
        prefix_len = len(settings.DATA_BLOB) + 1  # +1 for the slash "/"
        datasets_from_remote = {
            d.source_url[prefix_len:]: d.dataset_id for d in datasets_from_remote_query
        }

        # update the response with the newest dataset's id, if any
        for dataset in remote_datasets:
            id = datasets_from_remote.get(dataset["UniqueName"])
            if id:
                dataset["localDatasetID"] = id

        return remote_datasets

    @action(detail=False, methods=["GET"])
    def remote_with_categories(self, request):
        response = {
            "categories": self.fetch_remote_categories(),
            "datasets": self.fetch_remote_datasets_list(),
        }
        return Response(response, 201)

    @action(detail=False, methods=["GET"])
    def remote(self, request):
        entries = self.fetch_remote_datasets_list()
        return Response(entries, 201)

    @action(detail=False, methods=["POST"])
    def create_from_remote(self, request):
        name = get_optional_param(request, "name", f"New Dataset")
        remote_id = get_required_param(request, "id")
        project_id = get_project_from_request(request).project_id
        datatype = get_required_choice_param(request, "type", Dataset.Type.choices)
        destination = None if IS_CONTAINERIZED else request_path(request)

        with validation_conversion():
            task_id, dataset = Dataset.create_from_remote(
                request.user,
                project_id,
                name,
                remote_id,
                destination,
                datatype,
            )

        response = {
            "task_id": task_id,
            "dataset_id": dataset.dataset_id,
        }
        return Response(response, 201)

    @action(detail=False, methods=["POST"])
    def create_from_upload(self, request):
        if not is_upload_allowed():
            return HTTPExceptions.BAD_REQUEST.with_content(
                "This server isn't configured to allow uploads"
            )

        project_id = get_project_from_request(request).project_id

        file_uploaded = request.FILES.get("file_uploaded")
        if not file_uploaded:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file wasn't uploaded"
            )

        if not file_uploaded.name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file name wasn't provided."
            )

        dataset_name = request.POST.get("name")
        if not dataset_name:
            raise HTTPExceptions.BAD_REQUEST.with_content("name parameter is required")

        datatype = get_required_choice_post(request, "type", Dataset.Type.choices)
        if not datatype:
            raise HTTPExceptions.BAD_REQUEST.with_content("type parameter is required")

        with validation_conversion():
            task_id, dataset = Dataset.create_from_upload(
                request.user,
                project_id,
                dataset_name,
                datatype,
                file_uploaded.temporary_file_path(),
            )

        response = {
            "task_id": task_id,
            "dataset_id": dataset.dataset_id,
        }

        return Response(response, 201)

    @action(detail=True, methods=["GET"])
    def content(self, request, pk):
        ds = Dataset.get_by_id(pk)
        num_rows = get_optional_int_param(request, "num_rows", 4)  # 5 rows, 0 indexed

        if num_rows <= 0:
            raise HTTPExceptions.BAD_REQUEST.with_content(
                "num_rows must be a non-negative integer."
            )
        all_rows = ds.get_csv_content(num_rows=num_rows)
        sliced = itertools.islice(all_rows, 0, num_rows)
        return json_response({"file_contents": list(sliced)})

    @action(detail=False, methods=["POST"])
    def create_classification_dataset(self, request):
        dataset_path = get_required_param(request, "dataset_path")
        project_id = get_project_from_request(request).project_id

        task_id, dataset = Dataset.create_classification_dataset(
            request.user, project_id, dataset_path
        )

        response = {
            "task_id": task_id,
            "dataset_id": dataset.dataset_id,
            "dataset_location": dataset.location,
        }
        return Response(response, 201)

    @action(detail=False, methods=["POST"])
    def create_segmentation_dataset(self, request):
        image_path = get_required_param(request, "image_path")
        mask_path = get_required_param(request, "mask_path")
        project_id = get_project_from_request(request).project_id
        task_id, dataset = Dataset.create_segmentation_dataset(
            request.user, project_id, image_path, mask_path
        )

        response = {
            "task_id": task_id,
            "dataset_location": dataset.location,
            "dataset_id": dataset.dataset_id,
        }
        return Response(response, 201)

    @action(detail=False, methods=["POST"])
    def create_classification_dataset_from_upload(self, request):
        if not is_upload_allowed():
            return HTTPExceptions.BAD_REQUEST.with_content(
                "This server isn't configured to allow uploads"
            )

        project_id = get_project_from_request(request).project_id

        file_uploaded = request.FILES.get("file_uploaded")
        if not file_uploaded:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file wasn't uploaded"
            )

        if not file_uploaded.name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file name wasn't provided."
            )

        dataset_name = request.POST.get("name")
        if not dataset_name:
            raise HTTPExceptions.BAD_REQUEST.with_content("name parameter is required")

        task_id, dataset = Dataset.create_classification_dataset_from_upload(
            request.user, project_id, dataset_name, file_uploaded.temporary_file_path()
        )
        response = {
            "task_id": task_id,
            "dataset_location": dataset.location,
            "dataset_id": dataset.dataset_id,
        }

        return Response(response, 201)

    @action(detail=False, methods=["POST"])
    def create_segmentation_dataset_from_upload(self, request):
        if not is_upload_allowed():
            return HTTPExceptions.BAD_REQUEST.with_content(
                "This server isn't configured to allow uploads"
            )

        project_id = get_project_from_request(request).project_id

        mask_data = request.FILES.get("mask_file")
        if not mask_data:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file wasn't uploaded"
            )

        if not mask_data.name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file name wasn't provided."
            )

        image_data = request.FILES.get("image_file")
        if not image_data:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file wasn't uploaded"
            )

        if not image_data.name:
            raise HTTPExceptions.UNPROCESSABLE_ENTITY.with_content(
                "A file name wasn't provided."
            )

        task_id, dataset = Dataset.create_segmentation_dataset_from_upload(
            request.user,
            project_id,
            image_data.temporary_file_path(),
            image_data.name,
            mask_data.temporary_file_path(),
            mask_data.name,
        )

        response = {
            "task_id": task_id,
            "dataset_location": dataset.location,
            "dataset_id": dataset.dataset_id,
        }

        return Response(response, 201)
