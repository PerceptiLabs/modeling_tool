import os
import json
import pytest
from perceptilabs.endpoints.base import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def basic_request():
    with open('perceptilabs/endpoints/network_data/test_request.json') as f:
        payload = json.load(f)
    yield payload


@pytest.fixture
def basic_response():
    with open('perceptilabs/endpoints/network_data/test_response.json') as f:
        response = json.load(f)
    yield response


def test_basic(client, basic_request, basic_response):
    response = client.post(
        '/network_data',
        json=basic_request
    )
    assert response.json == basic_response



def test_previews_all_basic(client, basic_request):
    response = client.post(
        '/previews',
        json=basic_request
    )

    expected = {
        '0': {
            'Error': None,
            'VariableList': ['output'],
            'VariableName': 'output',
            'inShape': '[]'
        },
        '1': {
            'Error': None,
            'VariableList': ['output', 'W', 'b', 'preview'],
            'VariableName': 'output',
            'inShape': '[]'
        },
        '2': {
            'Error': None,
            'VariableList': ['output'],
            'VariableName': 'output',
            'inShape': '3'
        }
    }
    
    assert response.json == expected


def test_previews_one_basic(client, basic_request):
    response = client.post(
        '/previews/1',
        json=basic_request
    )

    expected = {
        'Error': None,
        'VariableList': ['output', 'W', 'b', 'preview'],
        'VariableName': 'output',
        'inShape': '[]'
    }

    assert response.json == expected
    
