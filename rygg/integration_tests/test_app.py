import pytest
import requests


@pytest.mark.timeout(0.2)
def test_version_is_public(host, port):
    url = f"http://{host}:{port}/app/version/?token=12312"
    resp = requests.get(url)
    assert resp.ok


@pytest.mark.timeout(0.2)
def test_isenterprise_is_public(host, port):
    url = f"http://{host}:{port}/app/is_enterprise/?token=12312"
    resp = requests.get(url)
    assert resp.ok


@pytest.mark.timeout(0.2)
def test_updates_available_is_public(host, port):
    url = f"http://{host}:{port}/app/updates_available/?token=12312"
    resp = requests.get(url)
    assert resp.ok
