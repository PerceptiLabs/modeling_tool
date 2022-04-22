from assertions import assert_eventually
from clients import ProjectClient, DatasetClient, ModelClient
from pathlib import Path
from rest import RyggRest
from contextlib import contextmanager

import http.client
import json
import pytest
import time
import urllib
import uuid


@pytest.fixture(scope="session")
def file_token():
    return "12312"


# allow for specifying the host on the pytest command line
def pytest_addoption(parser):
    parser.addoption("--host", action="store")
    parser.addoption("--port", action="store")
    parser.addoption("--path", action="store")
    parser.addoption("--vol_map", action="store")
    parser.addoption("--auth_env", action="store")


@pytest.fixture(scope="session")
def host(request):
    host_value = request.config.option.host
    if host_value is None:
        return "localhost"
    return host_value


@pytest.fixture(scope="session")
def port(request):
    port_value = request.config.option.port
    if port_value is None:
        return 8000
    return port_value


@pytest.fixture(scope="session")
def path(request):
    return request.config.option.path or ""


def token_from_keycloak(issuer, token_path, client_id, client_secret):
    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn = http.client.HTTPSConnection(issuer, context=ctx)
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    payload_encoded = urllib.parse.urlencode(payload)

    conn.request(
        "POST",
        token_path,
        payload_encoded,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    res = conn.getresponse()
    data_bytes = res.read()
    data_json = data_bytes.decode("utf-8")
    data = json.loads(data_json)
    token = data["access_token"]
    return token


def token_from_auth0(issuer, client_id, client_secret, api_audience):
    conn = http.client.HTTPSConnection(issuer)

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": api_audience,
        "grant_type": "client_credentials",
    }
    payload_json = json.dumps(payload)

    headers = {"content-type": "application/json"}

    conn.request("POST", "/oauth/token", payload_json, headers)

    res = conn.getresponse()
    data = res.read()

    as_json = data.decode("utf-8")
    as_dict = json.loads(as_json)
    ret = as_dict["access_token"]
    return ret


@pytest.fixture(scope="session")
def second_users_connection(host, port, path, file_token):
    second_auth_token = token_from_keycloak(
        "keycloak.dev.perceptilabs.com:8443",
        "/auth/realms/vue-perceptilabs/protocol/openid-connect/token",
        "integration-test-2",
        "e42a588e-dc44-4081-92fb-bbf45d20d639",
    )

    with make_rest(host, port, path, second_auth_token, file_token) as r:
        yield r


# It's imperative that this be session-scoped to avoid high costs with Auth0
@pytest.fixture(scope="session")
def auth_token(request):
    auth_env = request.config.option.auth_env or "dev"

    if auth_env == "dev":
        # set up keycloak following these directions: https://sahil-khanna.medium.com/rest-api-authentication-using-keycloak-b6afb07eceec
        return token_from_keycloak(
            "keycloak.dev.perceptilabs.com:8443",
            "/auth/realms/vue-perceptilabs/protocol/openid-connect/token",
            "integration-test",
            "c2ce91ea-ce06-493d-9a64-3cb31f1d298b",
        )

    elif auth_env == "pre_dev":
        return token_from_auth0(
            "dev-udw1gl-s.us.auth0.com",
            "rJHdjcTchMlXoCKaueAG22WTaGPJY9Fe",
            "aRGFo0lkmI4lLXb_jlXnnVeO6YOF_5O9gXzbpmIh9z2Y2cyGqDF2X5OnFoDZh5We",
            "https://ryggapi.perceptilabs.com/",
        )

    elif auth_env == "dev_a":
        return token_from_auth0(
            "dev-ymwf5efb.us.auth0.com",
            "tspKMSBOiGzoETUnJJFuvUySYI0OevZR",
            "i15s3u_A33TcBYuZHLBOA0qEQoN1mIC8gUAftmwSp5v2GSUa0ePlRZ9uAKnp5-D1",
            "https://backends-dev.perceptilabs.com/",
        )
    else:
        raise Exception(f"auth_env option is '{auth_env}'. Expected 'dev' or nothing.")


@pytest.fixture(scope="session")
def rest(host, port, path, auth_token, file_token):
    with make_rest(host, port, path, auth_token, file_token) as r:
        yield r


@contextmanager
def make_rest(host, port, path, auth_token, file_token):
    url = f"http://{host}:{port}{path}"
    with RyggRest(url, file_token, auth_token) as ret:
        assert_eventually(ret.check, stop_max_delay=60000, wait_fixed=1000)
        yield ret


@pytest.fixture(scope="session")
def vol_map(request):
    return request.config.option.vol_map or ""


@pytest.fixture(scope="session")
def to_local_translator(vol_map):
    if not vol_map:
        return lambda x: x

    def ret(remote_dir):
        local_prefix, remote_prefix = vol_map.split(":")
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
def tmp_file_path(tmpdir):
    assert tmpdir
    tmpdir_path = Path(tmpdir)
    assert tmpdir_path.is_dir()
    filename = "filename-" + uuid.uuid4().hex
    local_path = tmpdir_path.joinpath(filename)
    local_path.touch()
    yield local_path
    local_path.unlink()


@pytest.fixture
def tmp_file(tmp_file_path):
    yield str(tmp_file_path)


@pytest.fixture
def tmp_text_file_path(tmp_file_path):
    tmp_file_path.write_text("This is text")
    return tmp_file_path


@pytest.fixture
def tmp_text_file(tmp_file_path):
    return str(tmp_file_path)


@pytest.fixture
def tmp_utf8_file(tmp_file):
    # upload a UTF-8 file with a BOM
    CONTENT_STR = """
    this is some
    text
    """
    # construct a UTF-8 file with a BOM
    bytes = bytearray([0xEF, 0xBB, 0xBF])
    bytes.extend(CONTENT_STR.encode("ascii"))
    with open(tmp_file, "wb") as f:
        f.write(bytes)
    return tmp_file


MY_DIR = Path(__file__).parent

SPAM_CSV = MY_DIR.joinpath("test_data", "spam.csv")


@pytest.fixture
def tmp_dataset(tmp_text_file, rest, tmp_project):
    if rest.is_enterprise:
        _, dataset = DatasetClient.create_from_upload(
            rest, tmp_project, "new dataset", "M", SPAM_CSV
        )
        with dataset:
            yield dataset
    else:
        filename = tmp_text_file
        with DatasetClient.make(
            rest, name=filename, location=filename, project=tmp_project.id, type="M"
        ) as dataset:
            yield dataset


@pytest.fixture(scope="module")
def localhost_only(host):
    if host not in ["localhost", "127.0.0.1"]:
        pytest.skip()


@pytest.fixture(scope="module")
def pip_only(rest):
    if rest.is_enterprise:
        pytest.skip("local-only")


@pytest.fixture(scope="module")
def enterprise_only(rest):
    if not rest.is_enterprise:
        pytest.skip("enterprise-only")
