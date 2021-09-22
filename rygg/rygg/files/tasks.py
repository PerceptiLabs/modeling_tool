from celery import current_task
from celery.decorators import task
from celery.result import AsyncResult
from more_itertools import consume
from threading import Event, Thread
import logging
import os
import uuid

from rygg.celery import app as celery_app
from rygg.files.utils.download_data import download
from rygg.files.utils.sequences import observe_progress
from rygg.files.utils.zip import unzipped_files
from rygg.settings import IS_CONTAINERIZED

logger = logging.getLogger(__name__)

class LocalTasks():
    tasks = {}

    def add(task_id, thread, cancel_token):
        LocalTasks.tasks[task_id] = {
            "thread": thread,
            "cancel_token": cancel_token,
            "info": {
                "state": "PENDING",
            },
        }
        return task_id

    def update_state(task_id, state=None, meta=None):
        record = LocalTasks.tasks[task_id]
        if state:
            record["info"]["state"] = state

        if meta:
            record["info"]["meta"] = meta


    def get(task_id):
        return LocalTasks.tasks[task_id]["info"]

    def cancel(task_id):
        LocalTasks.tasks[task_id]["cancel_token"].set()


def get_celery_task_status(task_id):
    task = AsyncResult(task_id, app=celery_app)
    if task.info:
        if isinstance(task.info, Exception):
            return {"state": "failed"}

        return {"state": task.state, **task.info}
    elif task.successful():
        return {"state": "SUCCESS"}
    else:
        return None

def get_threaded_task_status(task_id):
    return LocalTasks.get(task_id)

def get_task_status(task_id):
    if IS_CONTAINERIZED:
        return get_celery_task_status(task_id)
    else:
        return get_threaded_task_status(task_id)

def cancel_task(task_id):
    if IS_CONTAINERIZED:
        celery_app.control.terminate(task_id)
    else:
        LocalTasks.cancel(task_id)

def do_unzip(filepath, status_fn):

    def progress(*args):
        status_fn(*args, "unzipping")

    # TODO: receive celery signals for canceling so we can set the token.
    cancel_token = Event()
    count, files = unzipped_files(filepath, cancel_token=cancel_token)
    observed = observe_progress(count, files, progress)
    consume(observed)

# Worker-side interface with celery
@task(
    name="unzip",
    bind=True,
)
def unzip_task(self, filepath):
    def update_status(expected, count, message):
        self.update_state(
            state='STARTED',
            meta={
                'expected_files': expected,
                'extracted_files': count,
                'message': message,
            }
        )

    do_unzip(filepath, update_status)


# Caller-side interface with Celery and/or threading
def unzip_async(filepath):
    task = celery_app.tasks["unzip"].delay(filepath)
    celery_app.backend.store_result(task.id, {"message": f"Queued unzip task for {filepath}"}, "PENDING")
    return task.id

@task(
    name="download",
    bind=True,
)
def download_task(self, link_url, dest_path):

    def update_status(expected, so_far, message):
        state = "STARTED"
        if expected == so_far:
            state = "SUCCESS"

        self.update_state(
            state=state,
            meta={
                'expected': expected,
                'so_far': so_far,
                'message': message,
            }
        )

    cancel_token = Event()

    download_unzip(link_url, dest_path, cancel_token, update_status)

def download_unzip(url, dest_folder, cancel_token, update_status_fn):

    file_path, chunk_count, chunks = download(url, dest_folder, cancel_token)

    increment = chunk_count / 50
    for ix, _ in enumerate(chunks):
        if ix % increment == 0:
            # Since we don't know how many files there are, we'll just double the chunks to approximate progress
            update_status_fn(chunk_count * 2, ix + 1, "Downloading")

    update_status_fn(chunk_count * 2, chunk_count, "Downloaded")

    unzipped_count, unzipped = unzipped_files(file_path, dest=dest_folder, cancel_token=cancel_token)
    total_steps = chunk_count + unzipped_count

    increment = unzipped_count / 50
    for ix, _ in enumerate(unzipped):
        if ix % increment == 0:
            update_status_fn(total_steps, ix + 1, "Unzipping")

    update_status_fn(total_steps, total_steps, "Complete")


def download_in_celery(link_url, dest_path):
    task = celery_app.tasks["download"].delay(link_url, dest_path)
    celery_app.backend.store_result(task.id, {"message": f"Queued download task for {link_url}"}, "PENDING")
    return task.id

def download_in_thread(link_url, dest_path):
    def update_status(expected, so_far, message):
        state = "STARTED"
        if expected == so_far:
            state = "SUCCESS"

        LocalTasks.update_state(
            task_id,
            state=state,
            meta={
                'expected': expected,
                'so_far': so_far,
                'message': message,
            }
        )

    cancel_token = Event()
    task_id = str(uuid.uuid4())
    def go():
        download_unzip(link_url, dest_path, cancel_token, update_status)
        LocalTasks.completed(task_id)

    t = Thread(target=go)
    task_id = LocalTasks.add(task_id, t, cancel_token)
    t.daemon = True
    t.start()
    return task_id

def download_async(link_url, dest_path):
    if IS_CONTAINERIZED:
        return download_in_celery(link_url, dest_path)
    else:
        return download_in_thread(link_url, dest_path)
