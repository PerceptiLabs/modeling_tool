from celery.decorators import task
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
    delete_path_task.delay(path)

@task
def delete_path_task(path):
    if _rm_rf(path):
        logger.info(f"Removed dataset at {path}")
