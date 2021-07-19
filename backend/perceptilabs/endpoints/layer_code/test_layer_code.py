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
    with open('perceptilabs/endpoints/layer_code/test_request.json') as f:
        payload = json.load(f)
    yield payload
    
    
@pytest.fixture
def basic_response():
    with open('perceptilabs/endpoints/layer_code/test_response.py_') as f:
        code = f.read()

    response = {'Output': code}
    yield response    
        
        
def test_basic(client, basic_request, basic_response):
    response = client.post('/layer_code', json=basic_request)
    assert response.json == basic_response


