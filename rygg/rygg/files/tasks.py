from __future__ import absolute_import, unicode_literals
import zipfile, os
from django.http import HttpResponse
from celery.decorators import task

import logging
logger = logging.getLogger(__name__)

@task
def unzipTask(filepath):
    dir_path = os.path.dirname(filepath)

    assert os.path.isfile(filepath)
    assert os.path.isdir(dir_path)

    with zipfile.ZipFile(filepath, 'r') as zip:
        zip.extractall(dir_path)
        files_extracted = zip.namelist()
        logger.info("file 1:", os.path.join(dir_path, files_extracted[0]))
