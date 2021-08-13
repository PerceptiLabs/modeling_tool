import pytest
import json
from perceptilabs.endpoints.base import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def basic_request():
    yield {'userEmail':"test@email.com"}

@pytest.fixture
def basic_response():
    yield "User has been set to test@email.com"

def test_basic(client, basic_request, basic_response):
    response = client.post('/set_user', json=basic_request)
    assert response.json == basic_response


