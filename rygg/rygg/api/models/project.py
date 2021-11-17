from django.db import models as dj_models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from model_utils.models import SoftDeletableModel
import os

from rygg.settings import IS_CONTAINERIZED, file_upload_dir
from rygg.api.tasks import delete_path_async


class Project(SoftDeletableModel):
    project_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    default_directory = dj_models.CharField(max_length=1000, blank=True)
    created = dj_models.DateTimeField(auto_now_add=True)
    updated = dj_models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.project_id})"

    @property
    def base_directory(self):
        if IS_CONTAINERIZED:
            return file_upload_dir(self.project_id)
        else:
            return self.default_directory

@receiver(post_save, sender=Project)
def project_created_post(created, instance, **kwargs):
    # we only manage the project dirs in docker
    if not IS_CONTAINERIZED:
        return

    dir = instance.base_directory

    if created:
        os.makedirs(dir, exist_ok=True)
    elif instance.is_removed:
        delete_path_async(instance.project_id, dir)
