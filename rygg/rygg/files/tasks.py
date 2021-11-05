import glob
import os

from rygg.files.utils.download_data import download
from rygg.files.utils.subprocesses import CanceledError
from rygg.files.utils.zip import unzipped_files
from rygg.tasks import run_async

# TODO: get this behind the tasks api
from celery.decorators import task
from rygg.tasks.celery import work_in_celery


######################
# Unzip
def unzip(cancel_token, status_callback, file_path):
    unzipped_count, unzipped = unzipped_files(file_path, cancel_token=cancel_token)
    for unzipped_ix, _ in enumerate(unzipped):
        status_callback(1, 0, "Unzipping", unzipped_count, unzipped_ix)


# Worker-side interface with celery
@task(
    name="unzip",
    bind=True,
)
def unzip_task(self, filepath):
    work_in_celery(self, unzip, filepath)


# Caller-side interface with Celery and/or threading
def unzip_async(filepath):
    return run_async("unzip", unzip, filepath)


######################
# Download/Unzip
@task(
    name="download",
    bind=True,
)
def download_task(self, dataset_id):
    work_in_celery(self, download_unzip, dataset_id)


def download_unzip(cancel_token, status_callback, dataset_id):
    from rygg.api.models import Dataset

    try:
        dataset = Dataset.objects.get(dataset_id=dataset_id)
    except Dataset.DoesNotExist:
        return
    dataset.status = "uploading"
    dataset.save()

    try:
        file_path, chunk_count, chunks = download(dataset.source_url, dataset.location, cancel_token)
        for chunk_ix, _ in enumerate(chunks):
            status_callback(2, 0, "Downloading", chunk_count, chunk_ix)

        unzipped_count, unzipped = unzipped_files(file_path, dest=dataset.location, cancel_token=cancel_token)
        for unzipped_ix, _ in enumerate(unzipped):
            status_callback(2, 1, "Unzipping", unzipped_count, unzipped_ix)

        glob_pattern = os.path.join(dataset.location, "**", "*.csv")
        matches = glob.glob(glob_pattern, recursive=True)
        if matches:
            dataset.status = "uploaded"
            dataset.location = matches[0]
        else:
            dataset.status = "failed: no data found"
        dataset.save()
    except CanceledError:

        # if we got here from an error or cancellation, then clean up
        if dataset:
            dataset.delete()

    except Exception as e:

        # if we got here from an error or cancellation, then clean up
        if dataset:
            dataset.delete()

        raise e

    finally:

        # remove the zip
        if os.path.exists(file_path):
            os.remove(file_path)


def download_async(dataset_id):
    return run_async("download", download_unzip, dataset_id)
