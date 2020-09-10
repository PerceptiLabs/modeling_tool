from contextlib import contextmanager
import json
import os
from shutil import rmtree

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
        yield f


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

