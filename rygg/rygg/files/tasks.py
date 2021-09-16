import zipfile, os
from celery.decorators import task

import logging
logger = logging.getLogger(__name__)

@task(name="unzip")
def unzipTask(filepath):
    dir_path = os.path.dirname(filepath)

    assert os.path.isfile(filepath)
    assert os.path.isdir(dir_path)

    with zipfile.ZipFile(filepath, 'r') as zip:
        zip.extractall(dir_path)
        files_extracted = zip.namelist()
        if files_extracted:
            logger.info(f"unzipped {len(files_extracted)} file(s). First one: {os.path.join(dir_path, files_extracted[0])}")
