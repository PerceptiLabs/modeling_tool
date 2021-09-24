from rygg.files.utils.download_data import download
from rygg.files.utils.zip import unzipped_files
from rygg.settings import IS_CONTAINERIZED
from rygg.tasks import run_async, get_task_status, cancel_task

# TODO: get this behind the tasks api
from celery.decorators import task
from rygg.tasks.celery import work_in_celery

######################
# Unzip
def unzip(cancel_token, file_path):
    unzipped_count, unzipped = unzipped_files(file_path, cancel_token=cancel_token)
    yield (1, "Unzipping", unzipped_count, unzipped)

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
def download_task(self, link_url, dest_path):
    work_in_celery(self, download_unzip, link_url, dest_path)

def download_unzip(cancel_token, url, dest_folder):
    file_path, chunk_count, chunks = download(url, dest_folder, cancel_token)
    yield (2, "Downloading", chunk_count, chunks)

    unzipped_count, unzipped = unzipped_files(file_path, dest=dest_folder, cancel_token=cancel_token)
    yield (2, "Unzipping", unzipped_count, unzipped)


def download_async(link_url, dest_path):
    return run_async("download", download_unzip, link_url, dest_path)
