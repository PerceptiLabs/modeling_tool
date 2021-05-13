from contextlib import contextmanager
import json
import os
from shutil import rmtree
import tempfile

@contextmanager
def local_file_cleanup(name):
    try:
        yield name
    finally:
        if os.path.isfile(name):
            os.remove(name)

@contextmanager
def local_dir_cleanup(name):
    try:
        yield name
    finally:
        if os.path.isdir(name):
            rmtree(name, ignore_errors=True)


@contextmanager
def temp_local_file(name, content):
    full_name = os.path.join(os.getcwd(), name)
    with open(full_name, "w") as f:
        f.write(content)

    with local_file_cleanup(full_name) as f:
        yield full_name


@contextmanager
def temp_local_dir(name):
    full_name = os.path.join(os.getcwd(), name)
    os.mkdir(full_name)
    with local_dir_cleanup(name) as d:
        yield d


@contextmanager
def temp_json_file(name, content):
    as_json = json.dumps(content)
    with temp_local_file(name, as_json) as f:
        yield f

@contextmanager
def temp_read_only(name):
    prev = os.stat(name).st_mode
    try:
        os.chmod(name, 0o0)
        yield
    finally:
        os.chmod(name, prev)

def cwd():
    return os.getcwd()

@contextmanager
def populated_tempfile(content_str):
    content_bytes=bytearray(content_str.encode('utf-8'))

    with tempfile.TemporaryDirectory() as td:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=td) as f:
            f.write(content_bytes)
            f.close()
            yield f.name

