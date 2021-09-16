import os
from celery.decorators import task
from rygg.files.utils.unzipper import Unzipper
from rygg.celery import app as celery_app
from threading import Event

import logging
logger = logging.getLogger(__name__)

@task(
    name="unzip",
    bind=True,
)
def unzip_task(self, filepath):
    dir_path = os.path.dirname(filepath)

    assert os.path.isfile(filepath)
    assert os.path.isdir(dir_path)

    cancel_token = Event()

    def update_status(expected, count, message):
        self.update_state(
            state='STARTED',
            meta={
                'expected_files': expected,
                'extracted_files': count,
                'message': message,
            }
        )

    unzipper = Unzipper(filepath, dir_path)
    cancel_token = unzipper.run(cancel_token, update_status)
    self.update_state(state='SUCCESS')

def unzip_async(filepath):
    task = celery_app.tasks["unzip"].delay(filepath)
    celery_app.backend.store_result(task.id, {"message": f"Queued unzip task for {filepath}"}, "PENDING")
    return task.id
