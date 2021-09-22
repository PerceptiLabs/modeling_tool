import os
import json
import pytest
from perceptilabs.endpoints.base import create_app
from perceptilabs.endpoints.session.threaded_executor import ThreadedExecutor
from retrying import retry


@pytest.fixture(scope='function')
def executor():
    ret = ThreadedExecutor()
    yield ret
    ret.dispose()

@pytest.fixture
def client(executor):
    app = create_app(session_executor=executor)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def basic_request():
    with open('perceptilabs/endpoints/session/test_request.json') as f:
        payload = json.load(f)
    yield payload


def test_sessions_list_is_empty_by_default(client):
    response = client.get('/session/list?user_email=anton.k@perceptilabs.com')

    assert response.status_code == 200
    assert response.json == {}


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def wait_for_active_task(client):
    response = client.get('/session/list?user_email=anton.k@perceptilabs.com')
    assert response.json != {}

@pytest.mark.skip(reason="does not return")
def test_session_start_returns_success(client, basic_request):
    response = client.post('/session/start', json=basic_request)
    assert response.status_code == 200

    got = response.json
    assert got.get("content") == "core started"

    wait_for_active_task(client)

    response = client.delete('/session?user_email=anton.k@perceptilabs.com&receiver=615')
    assert response.json != {}

    response = client.get('/session/list?user_email=anton.k@perceptilabs.com')
    assert response.json == {}

