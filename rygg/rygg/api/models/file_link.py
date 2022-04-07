from django.db import models as dj_models


class FileLink(dj_models.Model):
    filelink_id = dj_models.AutoField(primary_key=True)
    resource_locator = dj_models.CharField(max_length=1000, blank=False)
