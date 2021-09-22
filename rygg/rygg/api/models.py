from django.db import models as dj_models
from django.core.exceptions import ValidationError
from model_utils.models import SoftDeletableModel, StatusModel, TimeStampedModel
from model_utils import Choices
from django.dispatch import receiver
from django.db.models.signals import post_save
from rygg.settings import IS_CONTAINERIZED, FILE_UPLOAD_DIR, IS_SERVING
from rygg.api.tasks import delete_path
import os


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
        raise ValidationError(f"File {location} doesn't exist.", code=400)

class Dataset(SoftDeletableModel, StatusModel, TimeStampedModel):
    # On enterprise, the client is expected to upload the file afterward so the default status is "new".
    # On local, the file is expected to already exist so the default is "uploaded"
    STATUS = Choices('new', 'uploading', 'uploaded')

    # only set STATUS to something else when we're running, lest we confuse the migrations system
    if IS_SERVING and not IS_CONTAINERIZED:
        STATUS = Choices("uploaded")


    project = dj_models.ForeignKey(
        Project, related_name="datasets", on_delete=dj_models.PROTECT
    )
    dataset_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    location = dj_models.CharField(max_length=1000, blank=True, validators=[validate_file_name, validate_file_exists])

    def __str__(self):
        return f"{self.name} ({self.dataset_id})"

    class Meta:
        unique_together = (("project", "name"),
                           ("project", "location"))

    models = dj_models.ManyToManyField(Model, blank=True, related_name="datasets")

@receiver(post_save, sender=Dataset)
def dataset_deleted(sender, **kwargs):
    ds = kwargs["instance"]
    if ds.is_removed:
        # Only delete the file when we're in enterprise mode. We don't own the files in local mode
        if IS_CONTAINERIZED:
            file_path = os.path.join(FILE_UPLOAD_DIR, ds.location)
            delete_path(file_path)
