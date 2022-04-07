from django.core.exceptions import ValidationError
from django.db import models as dj_models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_http_exceptions import HTTPExceptions
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import SoftDeletableModel, StatusModel, TimeStampedModel
import os
import shutil
import uuid

from rygg.api.tasks import delete_path_async
from rygg.files.tasks import (
    download_async,
    unzip_async,
    create_classification_csv_async,
    create_segmentation_csv_async,
    classification_from_upload_async,
    segmentation_from_upload_async,
)
from rygg.settings import IS_CONTAINERIZED, file_upload_dir, IS_SERVING, DATA_BLOB
from rygg.api.models import Project, Model
from rygg.files.utils.file import get_text_lines


UPLOAD_PREFIX = "upload: "


def validate_file_name(location):
    # in local mode, we need to save the file's exact location
    if not IS_CONTAINERIZED:
        return

    if os.sep in location:
        raise ValidationError(
            f"File {location} contains an invalid character.", code=400
        )


def validate_file_exists(location):
    # on enterprise, the client is expected to upload the file afterward. On local, the file is expected to already exist.
    if IS_CONTAINERIZED:
        return

    if not os.path.isfile(location):
        raise ValidationError(f"File {location} isn't a file.", code=400)


def validate_root_dir(location):
    # on local we don't need the root dir. Skip validation
    if not IS_CONTAINERIZED:
        return

    if os.sep in location:
        raise ValidationError(
            f"Directory {location} contains an invalid character.", code=400
        )


def take_temp_file(tempfile_path, dest_dir, filename):
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, filename)
    shutil.copyfile(tempfile_path, dest_path)

    return dest_path


class Dataset(SoftDeletableModel, StatusModel, TimeStampedModel):
    # On enterprise, the client is expected to upload the file afterward so the default status is "new".
    # On local, the file is expected to already exist so the default is "building csv"
    STATUS = Choices("new", "uploading", "building csv", "uploaded")

    class Type(dj_models.TextChoices):
        CLASSIFICATION = "C", _("classification")
        SEGMENTATION = "S", _("segmentation")
        MULTI_MODAL = "M", _("multimodal")
        OBJECT_DETECTION = "O", _("objectdetection")

    # set status to building csv initially. when the csv file exists, it will be updated to uploaded
    if IS_SERVING and not IS_CONTAINERIZED:
        STATUS = Choices("building csv", "uploaded")

    project = dj_models.ForeignKey(
        Project,
        related_name="datasets",
        on_delete=dj_models.PROTECT,
    )
    dataset_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    location = dj_models.TextField(
        blank=True, validators=[validate_file_name, validate_file_exists]
    )
    source_url = dj_models.TextField(blank=True)
    models = dj_models.ManyToManyField(Model, blank=True, related_name="datasets")
    root_dir = dj_models.CharField(
        max_length=1000, blank=True, validators=[validate_root_dir]
    )
    type = dj_models.CharField(max_length=1, choices=Type.choices)

    def get_by_id(id):
        return Dataset.available_objects.get(pk=id, project__is_removed=False)

    def get_queryset():
        return Dataset.available_objects.filter(project__is_removed=False)

    def unregister(dataset_id):
        Dataset.get_by_id(dataset_id).delete()

    def delete_from_disk(dataset):
        if os.path.isfile(dataset.location) or os.path.isdir(dataset.location):
            full_path = dataset.location
            delete_path_async(dataset.project.project_id, full_path)

    @property
    def exists_on_disk(self):
        return os.path.isfile(self.location)

    @property
    def is_perceptilabs_sourced(self):
        return self.source_url and self.source_url.startswith(DATA_BLOB)

    @property
    def upload_path(self):
        if not self.source_url.startswith(UPLOAD_PREFIX):
            raise Exception(f"Dataset wasn't uploaded. Operation not supported.")

        prefix_len = len(UPLOAD_PREFIX)
        return self.source_url[prefix_len:]

    def get_csv_content(self, num_rows=4):
        if (
            not self.status == "uploaded"
            or not self.location
            or not os.path.isfile(self.location)
        ):
            raise Exception("Attempt to read contents before completion")

        return get_text_lines(self.location, num_rows=num_rows)

    def __str__(self):
        return f"{self.name} ({self.dataset_id})"

    class Meta:
        unique_together = (("project", "name"), ("project", "location"))

    @classmethod
    def create_from_remote(cls, project_id, name, remote_name, destination, type):
        if IS_CONTAINERIZED:
            upload_dir = file_upload_dir(project_id)
            unique_suffix = f"dataset-{uuid.uuid4()}"
            root_dir = os.path.join(upload_dir, unique_suffix)
        else:
            root_dir = destination

        dataset = Dataset(
            project_id=project_id,
            name=name,
            source_url=f"{DATA_BLOB}/{remote_name}",
            root_dir=root_dir,
            type=type,
        )

        dataset.save()
        task_id = download_async(dataset.dataset_id)

        return task_id, dataset

    @classmethod
    def create_from_upload(cls, project_id, dataset_name, type, uploaded_temp_file):
        if not IS_CONTAINERIZED:
            raise Exception("Not supported!")

        upload_dir = file_upload_dir(project_id)
        dest_dir = os.path.join(upload_dir, f"dataset-{uuid.uuid4()}")

        upload_path = take_temp_file(uploaded_temp_file, dest_dir, dataset_name)

        dataset = Dataset(
            project_id=project_id,
            name=dataset_name,
            location=upload_path,
            type=type,
            root_dir=dest_dir,  # a way to keep track of the fact that this was an upload
            source_url=f"{UPLOAD_PREFIX}{upload_path}",
        )
        dataset.save()
        task_id = unzip_async(dataset.dataset_id)

        return task_id, dataset

    @classmethod
    def create_segmentation_dataset_from_upload(
        cls,
        project_id,
        image_data_path,
        image_dataset_name,
        mask_data_path,
        mask_dataset_name,
    ):
        if not IS_CONTAINERIZED:
            raise Exception("Not supported!")

        upload_dir = file_upload_dir(project_id)
        dest_dir = os.path.join(upload_dir, f"dataset-{uuid.uuid4()}")

        dataset_name = image_dataset_name
        images_upload_path = take_temp_file(
            image_data_path, dest_dir, image_dataset_name
        )
        masks_upload_path = take_temp_file(mask_data_path, dest_dir, mask_dataset_name)
        location = dest_dir + "/" + "pl_data.csv"
        dataset = Dataset(
            project_id=project_id,
            name=dataset_name,
            location=location,  # csv location
            root_dir=dest_dir,  # a way to keep track of the fact that this was an upload
            source_url=f"{UPLOAD_PREFIX}{dest_dir}",  # there are two zip files. hence using the root directory
            type=cls.Type.SEGMENTATION,
        )
        dataset.save()
        task_id = segmentation_from_upload_async(
            dataset.dataset_id, images_upload_path, masks_upload_path
        )

        return task_id, dataset

    @classmethod
    def create_classification_dataset_from_upload(
        cls, project_id, dataset_name, uploaded_temp_file
    ):
        if not IS_CONTAINERIZED:
            raise Exception("Not supported!")

        upload_dir = file_upload_dir(project_id)
        dest_dir = os.path.join(upload_dir, f"dataset-{uuid.uuid4()}")
        upload_path = take_temp_file(uploaded_temp_file, dest_dir, dataset_name)
        dataset = Dataset(
            project_id=project_id,
            name=dataset_name,
            location=upload_path,  # dataset location (not particularly csv)
            root_dir=dest_dir,  # a way to keep track of the fact that this was an upload
            source_url=f"{UPLOAD_PREFIX}{upload_path}",
            type=cls.Type.CLASSIFICATION,
        )
        dataset.save()
        task_id = classification_from_upload_async(dataset.dataset_id)

        return task_id, dataset

    @classmethod
    def create_classification_dataset(cls, project_id, dataset_path):
        if IS_CONTAINERIZED:
            raise HTTPExceptions.NOT_FOUND

        location = dataset_path + "/" + "pl_data.csv"
        name = os.path.split(dataset_path)[1]

        datasetExist = (
            Dataset.get_queryset()
            .filter(project_id=project_id, name=name, location=location)  # csv location
            .exists()
        )

        if datasetExist:
            return None, Dataset.get_queryset().get(
                project_id=project_id, name=name, location=location
            )

        dataset = Dataset(
            project_id=project_id,
            name=name,
            location=location,
            type=cls.Type.CLASSIFICATION,
        )
        dataset.save()
        task_id = create_classification_csv_async(dataset, dataset_path)
        return task_id, dataset

    @classmethod
    def create_segmentation_dataset(cls, project_id, image_path, mask_path):
        if IS_CONTAINERIZED:
            raise HTTPExceptions.NOT_FOUND

        image_root_dir = os.path.split(image_path)[0]

        location = image_path + "/" + "pl_data.csv"
        name = os.path.split(image_root_dir)[1]

        datasetExist = (
            Dataset.get_queryset()
            .filter(project_id=project_id, name=name, location=location)
            .exists()
        )
        if datasetExist:
            return None, Dataset.get_queryset().get(
                project_id=project_id, name=name, location=location
            )

        dataset = Dataset(
            project_id=project_id,
            name=name,
            location=location,
            type=cls.Type.SEGMENTATION,
        )
        dataset.save()
        task_id = create_segmentation_csv_async(dataset, image_path, mask_path)
        return task_id, dataset


@receiver(pre_save, sender=Dataset)
def dataset_pre_save(sender, **kwargs):
    ds = kwargs["instance"]
    if ds.exists_on_disk:
        ds.status = "uploaded"
    # we're only modifying datasets that have been removed
    if not ds.is_removed:
        return

    unique_str = "_TO_DELETE_" + str(uuid.uuid4())

    # Make the name unique by appending a uuid. Allows making a new model with the same name.
    ds.name += unique_str

    # move the location for the same reason.
    new_location = ds.location + unique_str

    # also move the files just in case the client wants to create a new dataset in the same location right away, before the cleanup task runs
    # (but only in enterprise mode, where we own the files)
    if os.path.exists(ds.location) and ds.is_perceptilabs_sourced:
        shutil.move(ds.location, new_location)

    ds.location += unique_str


@receiver(post_save, sender=Dataset)
def dataset_post_save(sender, **kwargs):
    ds = kwargs["instance"]
    if ds.is_removed:
        # after unpacking, remote datasets have their path edited. Take that into account
        if os.path.isfile(ds.location):
            full_path = os.path.dirname(ds.location)
        elif os.path.isdir(ds.location):
            full_path = ds.location
        else:
            # It's not there. Bail out.
            return

        delete_path_async(ds.project.project_id, full_path)
    elif ds.root_dir:
        os.makedirs(ds.root_dir, exist_ok=True)
