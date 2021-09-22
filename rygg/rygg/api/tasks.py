from celery.decorators import task
from rygg.celery import app as celery_app
import os, shutil

import logging
logger = logging.getLogger(__name__)

def _rm_rf(path):

    # short-circuit
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True

    elif os.path.isfile(path):
        os.remove(path)
        return True

    return False

def delete_path(path):
    task = celery_app.tasks["delete_path"].delay(path)
    celery_app.backend.store_result(task.id, {"message": f"Queued delete_path task for {path}"}, "PENDING")
    return task.id

@task(
    name="delete_path",
    bind=True,
)
def delete_path_task(self, path):
    if _rm_rf(path):
        logger.info(f"Removed dataset at {path}")
