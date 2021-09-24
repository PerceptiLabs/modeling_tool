from contextlib import contextmanager
import logging
import os
import requests
import zipfile

from rygg.files.utils.subprocesses import CanceledError, cancelable_sequence

logger = logging.getLogger(__name__)

DOWNLOAD_CHUNK_SIZE = 1024 * 8

def iterate_in_context(sequence, contextmanager_fn, *args, **kwargs):
    try:
        cur = sequence.__next__()
        with contextmanager_fn(*args, **kwargs) as cm:
            while True:
                yield cur, cm
                cur = sequence.__next__()
    except StopIteration:
        pass

class DownloadFailedError(Exception):
    def __init__(self, url, status_code, text):
        Exception.__init__(f"Download from {url} failed: status code {status_code}\n{text}")

def get_data_chunks(url):
    r = requests.get(url, stream=True)
    if not r.ok:
        raise DownloadFailedError(url, r.status_code, r.text)

    num_bytes = int(r.headers.get("Content-Length", "0"))
    chunk_count = int(num_bytes / DOWNLOAD_CHUNK_SIZE) + 1 if num_bytes else None
    all_chunks = r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE)
    non_empty_chunks = (chunk for chunk in all_chunks if chunk)
    return chunk_count, non_empty_chunks

def write_chunks(chunks, file_path):

    @contextmanager
    def open_with_flush():
        dest_folder = os.path.dirname(file_path)
        os.makedirs(dest_folder, exist_ok=True)
        with open(file_path, 'wb') as f:
            yield f
            f.flush()
            os.fsync(f.fileno())

    for chunk, f in iterate_in_context(chunks, open_with_flush):
        f.write(chunk)
        yield chunk

def download(url, dest_folder, cancel_token=None):
    filename = url.split('/')[-1].replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    chunk_count, chunks = get_data_chunks(url)
    cancelable = cancelable_sequence(chunks, cancel_token)
    written = write_chunks(cancelable, file_path)
    return file_path, chunk_count, written
