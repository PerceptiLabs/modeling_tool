import os
import json
import pytest
from perceptilabs.endpoints.base import create_app
from perceptilabs.cache_utils import DictCache


@pytest.fixture(scope='function')
def metadata_cache():
    yield DictCache()

@pytest.fixture
def client(metadata_cache):
    app = create_app(data_metadata_cache=metadata_cache)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def basic_request():
    with open('perceptilabs/endpoints/data/test_request.json') as f:
        payload = json.load(f)
    yield payload
    

def test_data_is_inserted_to_cache(client, basic_request, metadata_cache):
    assert len(metadata_cache) == 0
    
    response = client.put(
        '/data',
        json=basic_request
    )
    assert response.status_code == 200
    assert len(metadata_cache) > 0


def test_data_is_available_in_cache(client, basic_request, metadata_cache):
    response = client.put(
        '/data',
        json=basic_request
    )

    assert response.status_code == 200
    dataset_hash = response.json["datasetHash"]

    response = client.get(f"/data?dataset_hash={dataset_hash}")    
    assert response.status_code == 200
    assert response.json == {"is_ready": "true"}
    

def test_data_is_unavailable_in_cache(client):
    response = client.get("/data?dataset_hash=abc")
    assert response.status_code == 204

    
