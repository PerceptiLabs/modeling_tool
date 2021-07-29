import os
import json
import pytest
from perceptilabs.endpoints.base import create_app
from perceptilabs.endpoints.session.threaded_executor import ThreadedExecutor


@pytest.fixture(scope='function')
def executor():
    yield ThreadedExecutor(single_threaded=True)

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


def test_session_start_returns_success(client, basic_request):
    response = client.post('/session/start', json=basic_request)

    assert response.status_code == 200
    assert response.json == {"content": "core started"}
    
    response = client.get('/session/list?user_email=anton.k@perceptilabs.com')
    assert response.json != {}
    
