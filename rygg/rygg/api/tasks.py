from celery.decorators import task
import os, shutil

from rygg.celery import app as celery_app
from rygg.settings import FILE_UPLOAD_DIR

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

def is_subdir(child, parent):
    if os.path.commonpath([parent, child]) != parent:
        return False

    if os.path.samefile(parent, child):
        return False

    return True

def delete_path(path):
    if not os.path.exists(path):
        return;

    full = os.path.abspath(path)

    # only allow deleting from inside the upload dir
    if not is_subdir(full, FILE_UPLOAD_DIR):
        raise Exception(f"'{path}' isn't available for deletion")

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
