import os
from pathlib import Path
import pytest
import time
import uuid

from rest import RyggRest
from assertions import assert_eventually
from clients import ProjectClient, DatasetClient, ModelClient

# allow for specifying the host on the pytest command line
def pytest_addoption(parser):
    parser.addoption("--host", action="store")


@pytest.fixture(scope='session')
def host(request):
    host_value = request.config.option.host
    if host_value is None:
        return "localhost"
    return host_value


@pytest.fixture(scope='session')
def rest(host):
    with RyggRest(f"http://{host}:8000", "12312") as ret:
        assert_eventually(ret.check, stop_max_delay=60000, wait_fixed=1000)
        yield ret


@pytest.fixture
def tmp_project(rest):
    with ProjectClient.make(rest, name="test project") as project:
        yield project


@pytest.fixture
def tmp_model(rest, tmp_project):
    with ModelClient.make(rest, project=tmp_project.id, name="model name") as model:
        yield model


@pytest.fixture
def tmp_file(tmpdir):
    assert tmpdir
    assert os.path.isdir(tmpdir)
    filename = "filename-" + uuid.uuid4().hex
    local_path = os.path.join(tmpdir, filename)
    Path(local_path).touch()
    yield local_path
    os.remove(local_path)


@pytest.fixture
def tmp_text_file(tmp_file):
    open(tmp_file, "w").write("This is text")
    return tmp_file

@pytest.fixture
def tmp_utf8_file(tmp_file):
    # upload a UTF-8 file with a BOM
    CONTENT_STR="""
    this is some
    text
    """
    # construct a UTF-8 file with a BOM
    bytes=bytearray([0xef, 0xbb, 0xbf])
    bytes.extend(CONTENT_STR.encode("ascii"))
    with open(tmp_file, "wb") as f:
        f.write(bytes)
    return tmp_file


@pytest.fixture
def tmp_dataset(tmp_text_file, rest, tmp_project):
    if rest.is_enterprise:
        filename = os.path.join(os.path.dirname(__file__), "spam.csv")
        _, dataset = DatasetClient.create_from_upload(rest, tmp_project, "new dataset", filename)
        with dataset:
            yield dataset
    else:
        filename = tmp_text_file
        with DatasetClient.make(rest, name=filename, location=filename, project=tmp_project.id) as dataset:
            yield dataset


@pytest.fixture(scope='module')
def localhost_only(host):
    if host not in ["localhost", "127.0.0.1"]:
        pytest.skip()


@pytest.fixture(scope='module')
def pip_only(rest):
    if rest.is_enterprise:
        pytest.skip("local-only")


@pytest.fixture(scope='module')
def enterprise_only(rest):
    if not rest.is_enterprise:
        pytest.skip("enterprise-only")


