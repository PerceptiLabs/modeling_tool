from django.db import models as dj_models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from model_utils.models import SoftDeletableModel
import json
import os
import re
import uuid

from rygg.api.models import Project
from rygg.api.tasks import delete_path_async
from rygg.settings import IS_CONTAINERIZED, file_upload_dir


def load_json(full_path):
    with open(full_path, "r") as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            return None


def save_json(full_path, as_dict):
    with open(full_path, "w") as f:
        json.dump(as_dict, f)
    assert os.path.isfile(full_path)


class Model(SoftDeletableModel):
    # TODO: make the json required on creation

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

    def get_queryset(user):
        user_filters = {}
        if IS_CONTAINERIZED:
            allowed_users = [Project.GRANDFATHERED_OWNER, user.username]
            user_filters = dict(project__owner__in=allowed_users)

        return Model.available_objects.filter(project__is_removed=False, **user_filters)

    @property
    def abs_dir(self):
        assert self.location
        return os.path.expanduser(self.location)

    @property
    def full_location(self):
        return os.path.join(self.abs_dir, "model.json")

    @property
    def content(self):
        full_path = self.full_location
        if not os.path.isfile(full_path):
            return None

        return load_json(full_path)

    def save_content(self, model_dict):
        assert not os.path.isdir(self.full_location)
        assert not self.abs_dir.endswith(".json")
        os.makedirs(self.abs_dir, exist_ok=True)

        if not os.path.isdir(self.abs_dir):
            raise PermissionError(f"Couldn't make {self.abs_dir}")

        if not os.access(self.abs_dir, os.W_OK):
            raise PermissionError(f"{self.abs_dir} is not writeable")

        if os.path.isfile(self.full_location) and not os.access(
            self.full_location, os.W_OK
        ):
            raise PermissionError(f"{self.full_location} is not writeable")

        save_json(self.full_location, model_dict)

    def next_name(project_id, prefix, user):
        models = (
            Model.get_queryset(user)
            .filter(project_id=project_id, name__startswith=prefix)
            .values("name")
        )
        if not models.exists():
            return f"{prefix} 1"

        names = [m["name"] for m in models]
        exp = re.compile(f"^{prefix} +(\d+)")

        matching_suffixes = [exp.split(d)[1] for d in names if exp.match(d)]
        as_ints = [int(x) for x in matching_suffixes] or [0]
        next_seq = max(as_ints) + 1
        return f"{prefix} {next_seq}"


# Create a directory for the model after it's created
@receiver(pre_save, sender=Model)
def model_pre_save(instance, **kwargs):
    if not IS_CONTAINERIZED:
        return

    # we're only interested in new models
    if instance.model_id != None:
        return

    parent_dir = file_upload_dir(instance.project_id)
    model_dir = f"model-{uuid.uuid4()}"
    instance.location = os.path.join(parent_dir, model_dir)
    assert instance.location
    os.makedirs(instance.abs_dir, exist_ok=True)


# Remove the model's files on deletion
@receiver(post_save, sender=Model)
def model_post_save(instance, **kwargs):
    if not IS_CONTAINERIZED:
        return

    if instance.is_removed:
        delete_path_async(instance.project.project_id, instance.abs_dir)
