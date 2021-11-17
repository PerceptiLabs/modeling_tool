from celery.decorators import task
import os
import shutil

from rygg.tasks import run_async
from rygg.settings import file_upload_dir, IS_CONTAINERIZED
from rygg.tasks.celery import work_in_celery

import logging
logger = logging.getLogger(__name__)

def _rm_rf(path):

    # short-circuit
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
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

def delete_path(cancel_token, status_callback, path):
    if _rm_rf(path):
        logger.info(f"Removed dataset at {path}")

def delete_path_async(project_id, path):
    if not os.path.exists(path):
        return;


    # only allow deleting from inside the upload dir
    if IS_CONTAINERIZED:
        full = os.path.abspath(path)
        upload_dir = file_upload_dir(project_id)
        parent_dir = os.path.dirname(upload_dir)
        if not full or not is_subdir(full, parent_dir):
            raise Exception(f"'{path}' isn't available for deletion")

    run_async("delete_path", delete_path, path)

@task(
    name="delete_path",
    bind=True,
)
def delete_path_task(self, path):
    work_in_celery(self, delete_path, path)
