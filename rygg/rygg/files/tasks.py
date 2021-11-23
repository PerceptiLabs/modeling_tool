from contextlib import contextmanager
import glob
import os

from rygg.files.utils.download_data import download
from rygg.files.utils.subprocesses import CanceledError
from rygg.files.utils.zip import unzipped_files
from rygg.tasks import run_async

# TODO: get this behind the tasks api
from celery import Celery
from rygg.tasks.celery import work_in_celery

app = Celery()


######################
# Utils
class DatasetOperationException(Exception):
    pass

@contextmanager
def dataset_operation(dataset_id):
    from rygg.api.models import Dataset

    dataset = Dataset.get_by_id(dataset_id)
    dataset.status = "processing"
    dataset.save()

    try:
        yield dataset
        dataset.status = "uploaded"
    except DatasetOperationException as e:
        dataset.status = f"failed: {e}"
        raise e
    except Exception as e:
        dataset.status = "failed"
        raise e
    finally:
        dataset.save()


def find_csv(root_dir):
    glob_pattern = os.path.join(root_dir, "**", "*.csv")
    matches = glob.glob(glob_pattern, recursive=True)

    if not matches:
        raise DatasetOperationException("no data found")

    return matches[0]


def rm_f(file):
    if os.path.exists(file):
        os.remove(file)

######################
# Unzip
def is_zip(file):
    return open(file, "rb").read(4) == b'PK\x03\x04'

def is_csv(file):
    content = open(file, "r").read(100)
    # very rudimentary check that it's csv
    return len(content) > 0 and "," in content


def unzip(cancel_token, status_callback, dataset_id):
    with dataset_operation(dataset_id) as dataset:
        filepath = dataset.upload_path

        # if the filepath is a zip, then unzip
        if is_zip(filepath):
            unzipped_count, unzipped = unzipped_files(filepath, dest=dataset.root_dir, cancel_token=cancel_token)
            for unzipped_ix, _ in enumerate(unzipped):
                status_callback(1, 0, "Unzipping", unzipped_count, unzipped_ix)

            # remove the zip
            rm_f(filepath)

            # point the dataset at the csv
            dataset.location = find_csv(dataset.root_dir)

        elif is_csv(filepath):
            os.makedirs(dataset.root_dir, exist_ok=True)
            dest = os.path.join(dataset.root_dir, "data.csv")
            os.rename(filepath, dest)
            dataset.location = dest


# Worker-side interface with celery
@app.task(
    name="unzip", # must be in list in rygg/celery.py
    bind=True,
)
def unzip_task(self, dataset_id):
    work_in_celery(self, unzip, dataset_id)


# Caller-side interface with Celery and/or threading
def unzip_async(dataset_id):
    return run_async("unzip", unzip, dataset_id)


######################
# Download/Unzip
@app.task(
    name="download", # must be in list in rygg/celery.py
    bind=True,
)
def download_task(self, dataset_id):
    work_in_celery(self, download_unzip, dataset_id)


def download_unzip(cancel_token, status_callback, dataset_id):
    from rygg.api.models import Dataset

    try:
        dataset = Dataset.objects.get(dataset_id=dataset_id)
        dataset.status = "uploading"
        dataset.save()
        file_path, chunk_count, chunks = download(dataset.source_url, dataset.root_dir, cancel_token)
        for chunk_ix, _ in enumerate(chunks):
            status_callback(2, 0, "Downloading", chunk_count, chunk_ix)

        if not os.path.isfile(file_path):
            raise Exception("Internal Error: downloading didn't generate a file")

        # re-fetch the dataset just in case it's been deleted
        dataset = Dataset.objects.get(dataset_id=dataset_id)

        unzipped_count, unzipped = unzipped_files(file_path, dest=dataset.root_dir, cancel_token=cancel_token)
        for unzipped_ix, _ in enumerate(unzipped):
            status_callback(2, 1, "Unzipping", unzipped_count, unzipped_ix)

        glob_pattern = os.path.join(dataset.root_dir, "**", "*.csv")
        matches = glob.glob(glob_pattern, recursive=True)
        if matches:
            dataset.status = "uploaded"
            dataset.location = matches[0]
        else:
            dataset.status = "failed: no data found"
        dataset.save()
    except Dataset.DoesNotExist:
        # if the dataset is missing, then we're done
        pass
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
