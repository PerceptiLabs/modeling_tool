import pytest
from perceptilabs.endpoints.base import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

        
def test_basic(client):
    csv_path = 'perceptilabs/endpoints/type_inference/test_data.csv'
    expected_response = {
        'x1': [['categorical', 'numerical'], 0],
        'y1': [['categorical', 'numerical'], 0]
    }
    response = client.get(f'/type_inference?path={csv_path}')
    assert response.json == expected_response


