import os
import json
import sys
import pytest
import tensorflow as tf

from perceptilabs.endpoints.base import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_version_request(client):
    response = client.get(f"/version")
    assert response.status_code == 200
    assert response.json == {'perceptilabs': 'development', 'python': sys.version, 'tensorflow': tf.__version__}
    
