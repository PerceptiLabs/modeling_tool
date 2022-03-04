from assertions import assert_eventually
from clients import ProjectClient, DatasetClient, ModelClient
from pathlib import Path
from rest import RyggRest

import http.client
import json
import os
import pytest
import time
import urllib
import uuid

# allow for specifying the host on the pytest command line
def pytest_addoption(parser):
    parser.addoption("--host", action="store")
    parser.addoption("--port", action="store")
    parser.addoption("--path", action="store")
    parser.addoption("--vol_map", action="store")
    parser.addoption("--auth_env", action="store")


@pytest.fixture(scope='session')
def host(request):
    host_value = request.config.option.host
    if host_value is None:
        return "localhost"
    return host_value

@pytest.fixture(scope='session')
def port(request):
    port_value = request.config.option.port
    if port_value is None:
        return 8000
    return port_value

@pytest.fixture(scope='session')
def path(request):
    return request.config.option.path or ""


@pytest.fixture(scope='session')
def auth_token(request):
    auth_env = request.config.option.auth_env or 'dev'

    if auth_env == 'dev':
        # set up keycloak following these directions: https://sahil-khanna.medium.com/rest-api-authentication-using-keycloak-b6afb07eceec
        AUTH_ISSUER = 'keycloak.dev.perceptilabs.com:8443'
        TOKEN_PATH = '/auth/realms/vue-perceptilabs/protocol/openid-connect/token'
        CLIENT_ID = 'integration-test'
        CLIENT_SECRET = 'c2ce91ea-ce06-493d-9a64-3cb31f1d298b'

        # TODO: Fix verification of the cert
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(AUTH_ISSUER, context=ctx)
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
        payload_encoded = urllib.parse.urlencode(payload)

        conn.request("POST", TOKEN_PATH, payload_encoded, headers={"content-type": "application/x-www-form-urlencoded"})

        res = conn.getresponse()
        data_bytes = res.read()
        data_json = data_bytes.decode("utf-8")
        data = json.loads(data_json)
        token = data['access_token']
        return token

    elif auth_env == 'prod':
        raise NotImplementedException("TODO")

    else:
        raise Exception(f"auth_env option is '{auth_env}'. Expected 'dev' or nothing.")



@pytest.fixture(scope='session')
def rest(host, port, path, auth_token):
    url=f"http://{host}:{port}{path}"
    with RyggRest(url, "12312", auth_token) as ret:
        assert_eventually(ret.check, stop_max_delay=60000, wait_fixed=1000)
        yield ret

@pytest.fixture(scope='session')
def vol_map(request):
    return request.config.option.vol_map or ""

@pytest.fixture(scope='session')
def to_local_translator(vol_map):
    if not vol_map:
        return lambda x: x

    def ret(remote_dir):
        local_prefix, remote_prefix = vol_map.split(':')
        n = remote_dir.replace(remote_prefix, local_prefix, 1)
        return n
    return ret


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
        _, dataset = DatasetClient.create_from_upload(rest, tmp_project, "new dataset", 'M', filename)
        with dataset:
            yield dataset
    else:
        filename = tmp_text_file
        with DatasetClient.make(rest, name=filename, location=filename, project=tmp_project.id, type='M') as dataset:
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
