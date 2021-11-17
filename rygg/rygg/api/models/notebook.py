from django.db import models as dj_models
from model_utils.models import SoftDeletableModel

from rygg.api.models import Project, FileLink

class Notebook(SoftDeletableModel):
    project = dj_models.ForeignKey(
        Project,
        related_name="notebooks",
        on_delete=dj_models.PROTECT
    )
    filelink = dj_models.ForeignKey(
        FileLink,
        related_name="notebook",
        on_delete=dj_models.SET_NULL,
        null=True
    )
    notebook_id = dj_models.AutoField(primary_key=True)
    name = dj_models.CharField(max_length=1000, blank=False)
    created = dj_models.DateTimeField(auto_now_add=True)
    updated = dj_models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.notebook_id})"
