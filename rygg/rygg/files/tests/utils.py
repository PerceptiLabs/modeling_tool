from contextlib import contextmanager
from shutil import rmtree
import json
import os
import tempfile
import uuid

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
def temp_file_abs_path(full_path, content):
    dirname = os.path.dirname(full_path)
    os.makedirs(dirname, exist_ok=True)
    assert os.path.isdir(os.path.dirname(full_path))
    as_json = json.dumps(content)
    with temp_local_file(full_path, as_json) as f:
        yield f

@contextmanager
def temp_json_file_abs_path(full_path, content):
    with temp_file_abs_path(full_path, content) as f:
        yield f

@contextmanager
def temp_json_file(rel_name, content):
    as_json = json.dumps(content)
    with temp_local_file(rel_name, as_json) as f:
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

class TempFileTester():
    def setUp(self):
        # Create a temporary directory
        self._test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        rmtree(self.test_dir, ignore_errors=True)

    def filename_in_temp_dir(self, filename=None):
        if not filename:
            filename = str(uuid.uuid4())

        return os.path.join(self.test_dir, filename)

    def file_in_temp_dir(self, filename=None, content=None):
        if not content:
            content = "this is some text"

        path = self.filename_in_temp_dir(filename)
        dir = os.path.dirname(path)
        os.makedirs(dir, exist_ok=True)
        open(path, "w").write(content)
        return path

    @property
    def test_dir(self):
        return self._test_dir

