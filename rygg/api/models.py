from django.db import models


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Model(models.Model):
    project = models.ForeignKey(
        Project, related_name="models", on_delete=models.PROTECT
    )
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
