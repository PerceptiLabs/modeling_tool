from django.db import models


class FileLink(models.Model):
    filelink_id = models.AutoField(primary_key=True)
    resource_locator = models.CharField(max_length=1000, blank=False)

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=False)
    default_directory = models.CharField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.project_id})"

class Model(models.Model):
    project = models.ForeignKey(
        Project, related_name="models", on_delete=models.PROTECT
    )
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=False)
    location = models.CharField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    saved_by = models.CharField(max_length=100, blank=True)
    saved_version_location = models.CharField(max_length=100, blank=True)

class Notebook(models.Model):
    project = models.ForeignKey(
        Project, related_name="notebooks", on_delete=models.PROTECT
    )
    filelink = models.ForeignKey(
        FileLink, related_name="notebook", on_delete=models.SET_NULL, null=True
    )
    notebook_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.notebook_id})"