from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rygg.settings")

app = Celery(
    "rygg",
    task_routes={
        "unzip": {"queue": "rygg"},
        "delete_path": {"queue": "rygg"},
        "download": {"queue": "rygg"},
        "classification_from_upload": {"queue": "rygg"},
        "segmentation_from_upload": {"queue": "rygg"},
    },
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
