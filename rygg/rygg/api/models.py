from django.core.exceptions import ValidationError
from django.db import models as dj_models
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django_http_exceptions import HTTPExceptions
from model_utils import Choices
from model_utils.models import SoftDeletableModel, StatusModel, TimeStampedModel
import glob
import os
import shutil
import uuid

from rygg.api.tasks import delete_path
from rygg.files.tasks import download_async
from rygg.settings import IS_CONTAINERIZED, FILE_UPLOAD_DIR, IS_SERVING, DATA_BLOB

class FileLink(dj_models.Model):
    filelink_id = dj_models.AutoField(primary_key=True)
    resource_locator = dj_models.CharField(max_length=1000, blank=False)

class Project(SoftDeletableModel):
    project_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    default_directory = dj_models.CharField(max_length=1000, blank=True)
    created = dj_models.DateTimeField(auto_now_add=True)
    updated = dj_models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.project_id})"

class Model(SoftDeletableModel):
    project = dj_models.ForeignKey(
        Project, related_name="models", on_delete=dj_models.PROTECT
    )
    model_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    location = dj_models.CharField(max_length=1000, blank=True)
    created = dj_models.DateTimeField(auto_now_add=True)
    updated = dj_models.DateTimeField(auto_now=True)
    saved_by = dj_models.CharField(max_length=100, blank=True)
    saved_version_location = dj_models.CharField(max_length=100, blank=True)

class Notebook(SoftDeletableModel):
    project = dj_models.ForeignKey(
        Project, related_name="notebooks", on_delete=dj_models.PROTECT
    )
    filelink = dj_models.ForeignKey(
        FileLink, related_name="notebook", on_delete=dj_models.SET_NULL, null=True
    )
    notebook_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    created = dj_models.DateTimeField(auto_now_add=True)
    updated = dj_models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.notebook_id})"

def validate_file_name(location):
    # in local mode, we need to save the file's exact location
    if not IS_CONTAINERIZED:
        return
    if os.sep in location:
        raise ValidationError(f"File {location} contains an invalid character.", code=400)


def validate_file_exists(location):
    # on enterprise, the client is expected to upload the file afterward. On local, the file is expected to already exist.
    if IS_CONTAINERIZED:
        return

    if not os.path.isfile(location):
        raise ValidationError(f"File {location} isn't a file.", code=400)

class Dataset(SoftDeletableModel, StatusModel, TimeStampedModel):
    # On enterprise, the client is expected to upload the file afterward so the default status is "new".
    # On local, the file is expected to already exist so the default is "uploaded"
    STATUS = Choices('new', 'uploading', 'uploaded')

    # only set STATUS to something else when we're running, lest we confuse the migrations system
    if IS_SERVING and not IS_CONTAINERIZED:
        STATUS = Choices("uploaded")


    project = dj_models.ForeignKey(
        Project,
        related_name="datasets",
        on_delete=dj_models.PROTECT,
    )
    dataset_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    location = dj_models.TextField(blank=True, validators=[validate_file_name, validate_file_exists])
    source_url = dj_models.TextField(blank=True)
    models = dj_models.ManyToManyField(Model, blank=True, related_name="datasets")

    @property
    def exists_on_disk(self):
        ret = os.path.isfile(self.location)
        return ret


    def __str__(self):
        return f"{self.name} ({self.dataset_id})"


    class Meta:
        unique_together = (("project", "name"),
                           ("project", "location"))


    def destroy(self, request, *args, **kwargs):
        # TODO: block request when the dataset is still downloading
        raise HTTPExceptions.BAD_REQUEST.with_content("Nope")
        super().destroy(request, *args, **kwargs)

    @classmethod
    def create_from_remote(cls, project_id, name, remote_name, destination):
        if IS_CONTAINERIZED:
            dest_path = os.path.join(FILE_UPLOAD_DIR, f"dataset-{uuid.uuid4()}")
        else:
            dest_path = destination

        dataset = Dataset(
            project_id=project_id,
            name=name,
            source_url=f"{DATA_BLOB}/{remote_name}",
            location=dest_path
        )
        dataset.save()
        task_id = download_async(dataset.dataset_id)

        return task_id, dataset


@receiver(pre_delete, sender=Dataset)
def dataset_deleted_pre(sender, **kwargs):
    ds = kwargs["instance"]
    # TODO: fail when the dataset isn't done unpacking yet. (Or make sure the task is abandoned)
    # TODO: ... or see whether renaming the directory below just breaks the download/unzip and upload/unzip tasks.
    # if ds.status

    unique_str = "_TO_DELETE_" + str(uuid.uuid4())

    # Make the name unique by appending a uuid. Allows making a new model with the same name.
    ds.name += unique_str

    # move the location for the same reason.
    new_location = ds.location + unique_str

    # also move the files just in case the client wants to create a new dataset in the same location right away, before the cleanup task runs
    # (but only in enterprise mode, where we own the files)
    if os.path.exists(ds.location) and IS_CONTAINERIZED:
        shutil.move(ds.location, new_location)

    ds.location += unique_str


@receiver(post_delete, sender=Dataset)
def dataset_deleted_post(sender, **kwargs):
    ds = kwargs["instance"]
    # Only delete the directory when we're in enterprise mode.
    # we also don't know the root dir except for files with a source_url, so only delete them
    if ds.source_url:
        full_path = os.path.dirname(ds.location)
        delete_path(full_path)
