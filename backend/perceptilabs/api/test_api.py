import os
import pytest
import pandas as pd
from unittest.mock import MagicMock
from retrying import retry
from unittest.mock import patch

from celery.contrib.pytest import (
    celery_worker, celery_app, celery_config,
    celery_parameters, celery_enable_logging,
    use_celery_app_trap, celery_includes,
    celery_worker_pool, celery_worker_parameters
)


from perceptilabs.caching.utils import DictCache
from perceptilabs.api.base import create_app
from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor
import perceptilabs.settings as settings


def make_session_id(string):
    import base64    
    return base64.urlsafe_b64encode(string.encode()).decode()


# TODO: session IDs [both training and testing] should be created in the Kernel... As a hack, just aask for the checkpoint directory on "start training" and "start testing", then the frontend can keep track of the returned session IDs.

@pytest.fixture(scope='function', autouse=True)
def mixpanel_mock(monkeypatch):
    fn_track = MagicMock()
    fn_set_once = MagicMock()
    fn_set = MagicMock()    

    from mixpanel import Mixpanel
    monkeypatch.setattr(Mixpanel, 'track', fn_track, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set_once', fn_set_once, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set', fn_set, raising=True)        

    return Mixpanel


@pytest.fixture(scope='function')
def user_token():
    return """eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI2YWtvOXRBdDFINlBZLXhKUzN0VWs3OXVBSVNqbkFxYjdyVGZYdklGQXBBIn0.eyJleHAiOjE2Mzk0MTkzMzIsImlhdCI6MTYzODgxNDUzMiwiYXV0aF90aW1lIjoxNjM4ODE0NTI5LCJqdGkiOiJiMzY4MTFhMi05ZGMxLTRkODktOWQ2ZS04MWU1MmM4NWQyZTgiLCJpc3MiOiJodHRwczovL2tleWNsb2FrLmRldi5wZXJjZXB0aWxhYnMuY29tOjg0NDMvYXV0aC9yZWFsbXMvdnVlLXBlcmNlcHRpbGFicyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI0Yzg3OTczMS01OWQzLTQ4YjQtYjFmNC00ODhmN2FkN2E4MDQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ2dWUtcGVyY2VwdGlsYWJzLWNsaWVudC1pZCIsIm5vbmNlIjoiODdjNzRiNzctNGM5Yy00OTMyLThjZGItN2ViNzVkMzQ3N2M5Iiwic2Vzc2lvbl9zdGF0ZSI6IjI3ODhmMGU1LTVjMjktNDhiZC1iMzEwLTViZTZlNGI2OGVmNSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDo4MDgwIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJzdCBsb2dpbiI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImFudG9uLmtAcGVyY2VwdGlsYWJzLmNvbSIsImVtYWlsIjoiYW50b24ua0BwZXJjZXB0aWxhYnMuY29tIn0.fG2nvdRjIuKYt2snGNK-z1OOq0bf4cguwPQUVPztoM9vxXUwibW-Tsy1IWH7jwSypTRLCzbbDQPVN6LqgonBBJar_YbIGpGex-qbli6yrsiRJMGS1fvxA4XfMjNd3cTojercm6PdYDvQ2rBcmjrbJoBXjxWGfN0ygq9vqzY_2UDb5RUlYWbITjddReVtJcDLkDKXo-xoow8jP49vn8KX9c-pBLIhxuPZG4AmNCVOp6_-3f4BoLhrwvKSsr45kOvscfVz2uwTr5QKiYbiHLzb28qax70V144vbIvOmRw1Ny2hOLb3eol8USJBn6JGw6VDjQUPjVCMwn4IPIQGZZ1Zkg"""


@pytest.fixture(scope='function', autouse=True)
def rygg_mock(monkeypatch, tmp_path):
    df = pd.DataFrame({
        'x1': [1.0, 2.0, 3.0, 4.0],
        'x2': [5.0, 6.0, 3.0, 9.0],
        'y1': ['a', 'b', 'c', 'd']
    })

    location = os.path.join(tmp_path, 'data.csv')
    df.to_csv(location, index=False)
    
    def get_dataset(self, dataset_id):
        response = {
            'location': location,
            'name': 'MyDataset',
            'is_perceptilabs_sourced': True                        
        }
        return response

    from perceptilabs.rygg import RyggWrapper
    monkeypatch.setattr(RyggWrapper, 'get_dataset', get_dataset)    
    

@pytest.fixture(scope='function')
def client(request, celery_worker):
    if not hasattr(request, 'param') or request.param == 'threaded':
        task_executor = ThreadedTaskExecutor()
    elif request.param == 'celery':
        task_executor = CeleryTaskExecutor(app=celery_worker.app)
    else:
        raise ValueError

    app = create_app(task_executor=task_executor)
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

        
@pytest.fixture
def dataset_settings():
    dict_ = {
        "featureSpecs": {
            "x1": {
                "iotype": "input",
                "datatype": "numerical",
                "preprocessing": {}
            },
            "x2": {
                "iotype": "do not use",
                "datatype": "numerical",
                "preprocessing": {}
            },
            "y1": {
                "iotype": "target",
                "datatype": "categorical",
                "preprocessing": {}
            }
        },
        "partitions": [
            70,
            20,
            10
        ],
        "randomizedPartitions": True,
        "datasetId": 123,
        "randomSeed": 123      
    }
    return dict_


@pytest.fixture
def training_settings():
    yield {
        'Epochs': 10,
        'Batch_size': 2,
        'Learning_rate': 0.001,
        'Beta1': 0.9,
        'Beta2': 0.99,
        'Momentum': 0.0,
        'Centered': False,
        'Loss': 'Quadratic',
        'Optimizer': 'SGD',
        'Shuffle': False,
        'AutoCheckpoint': False
    }


def has_been_called_with(func, args=None, kwargs=None, allow_subset=True):

    def cmp_kwargs(a, b):
        if allow_subset:
            for k in a.keys():
                if k not in b or b[k] != a[k]:
                    return False
            return True                                
        else:
            return a == b    

    for call_args in func.call_args_list:
        if args and kwargs:
            if args == call_args[0] and cmp_kwargs(kwargs, call_args[1]):
                return True
        elif args and not kwargs:
            if args == call_args[0]:
                return True
        elif kwargs and not args:
            if cmp_kwargs(kwargs, call_args[1]):
                return True
            
    return False


def assert_export(client, mixpanel_mock, user_token, dataset_settings, network, user_email, model_id, training_session_id, tmp_path):
    res = client.put(
        f'/models/{model_id}/export?training_session_id={training_session_id}', 
        json={
            'network': network,
            'datasetSettings': dataset_settings,
            'exportSettings': {
                'Location': str(tmp_path),
                'name': 'my-model',
                'Type': 'TFModel',
                'Compressed': False,
                'Quantized': False,
                'ExcludePreProcessing':False,
                'ExcludePostProcessing':False
            },
            'userEmail': user_email
        },
        headers={'Authorization': user_token}        
    )

    expected_path = os.path.join(tmp_path, 'my-model')
    
    assert res.status_code == 200
    assert res.json == f"Model exported to '{expected_path}'"

    assert set(os.listdir(expected_path)) == set([
        'saved_model.pb', 'variables', 'keras_metadata.pb', 'assets'])

    assert has_been_called_with(
        mixpanel_mock.track,
        kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'model-exported'}
    )

def assert_serving(client, mixpanel_mock, user_token, dataset_settings, network, user_email, model_id, training_session_id):
    res = client.post(
        f'/inference/serving/{model_id}?training_session_id={training_session_id}', 
        json={
            'settings': {'ExcludePreProcessing': False, 'ExcludePostProcessing': False},
            'network': network,
            'datasetSettings': dataset_settings,
            'modelName': 'my-model',
            'userEmail': user_email
        },
        headers={'Authorization': user_token}                
    )
    assert res.status_code == 200
    serving_session_id = res.json


    def has_expired(last_update):
        from datetime import datetime
        current_time = datetime.now().timestamp()  # Current unix time
        time_since_update = current_time - last_update
        
        return time_since_update > 2 * settings.SERVING_RESULTS_REFRESH_INTERVAL
    
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_serving_up():
        res = client.get(
            f"/inference/serving/{serving_session_id}/status",
            headers={'Authorization': user_token}                    
        )
        assert res.status_code == 200
        assert 'url' in res.json
        assert not has_expired(res.json['last_update'])

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'model-exported'}
        )

    wait_for_serving_up()                    

    res = client.post(
        f"/inference/serving/{serving_session_id}/stop",
        headers={'Authorization': user_token}
    )
    assert res.status_code == 200
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_serving_down():
        res = client.get(
            f"/inference/serving/{serving_session_id}/status",
            headers={'Authorization': user_token}
        )
        assert res.status_code == 200
        assert has_expired(res.json['last_update'])        
    
    wait_for_serving_down()            

    
def assert_data(client, dataset_settings):
    # Start preprocessing the dataset
    res = client.put(
        '/datasets/preprocessing',
        json={'datasetSettings': dataset_settings},
        headers={'Authorization': user_token}                
    )
    assert res.status_code == 200
    assert 'preprocessingSessionId' in res.json

    preprocessing_session_id = res.json['preprocessingSessionId']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_data():
        res = client.get(
            f"/datasets/preprocessing/{preprocessing_session_id}",
            headers={'Authorization': user_token}                    
        )  
        assert res.status_code == 200    
        assert res.json == {'is_complete': True, 'message': "Build status: 'complete'", 'error': None}

    wait_for_data()        


def assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings):
    # Get a model recommendation
    res = client.post(
        '/models/recommendations',
        json={'datasetSettings': dataset_settings},
        headers={'Authorization': user_token}
    )    
    assert res.status_code == 200
    assert mixpanel_mock.track.call_args[1]['distinct_id'] == 'anton.k@perceptilabs.com'
    assert mixpanel_mock.track.call_args[1]['event_name'] == 'model-recommended'    

    network = res.json
    return network


def assert_info(client, model_id, dataset_settings, network, user_email):
    res = client.post(
        f'/models/{model_id}/layers/info',
        json={
            'datasetSettings': dataset_settings,
            'network': network,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}                
    )

    for layer_id, layer_info in res.json.items():
        assert 'inShape' in layer_info
        assert 'outShape' in layer_info

    for layer_id in ['0', '1', '2']:
        res = client.post(
            f'/models/{model_id}/layers/{layer_id}/info',
            json={
                'datasetSettings': dataset_settings,
                'network': network,
                'userEmail': user_email
            },
            headers={'Authorization': user_token}                    
        )
        assert 'inShape' in res.json
        assert 'outShape' in res.json        


def assert_previews(client, model_id, dataset_settings, network, user_email):
    res = client.post(
        f'/models/{model_id}/layers/previews',
        json={
            'datasetSettings': dataset_settings,
            'network': network,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}                
    )
    
    assert res.status_code == 200
    assert res.json['outputDims']['0'] == {'Dim': '1', 'Error': None}
    assert res.json['outputDims']['1'] == {'Dim': '2', 'Error': None}
    assert res.json['outputDims']['2'] == {'Dim': '2', 'Error': None}        

    assert 'series' in res.json['previews']['0']
    assert 'xLength' in res.json['previews']['0']

    assert 'series' in res.json['previews']['1']
    assert 'xLength' in res.json['previews']['1']
    
    assert 'series' in res.json['previews']['2']
    assert 'xLength' in res.json['previews']['2']


def assert_layer_code(client, model_id, network, user_email):
    res = client.post(
        f'/models/{model_id}/layers/1/code',
        json={
            'network': network,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}                
    )

    def is_valid_syntax(code):
        try:
            import ast
            ast.parse(code)
        except SyntaxError:
            return False
        else:
            return True
    
    assert res.status_code == 200
    assert is_valid_syntax(res.json['Output'])


def assert_training(client, mixpanel_mock, user_token, model_id, network, dataset_settings, training_settings, training_session_id, user_email):
    res = client.post(
        f'/models/{model_id}/training/{training_session_id}',
        json={
            'network': network,
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}

    @retry(stop_max_attempt_number=10, wait_fixed=1000)    
    def wait_for_training_started():
        res = client.get(f'/models/{model_id}/training/{training_session_id}/status')
        assert res.status_code == 200
        
        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-started'}
        )

    wait_for_training_started()

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_completed():
        res = client.get(f'/models/{model_id}/training/{training_session_id}/status')
        assert res.status_code == 200

        assert 'Epoch' in res.json        
        assert 'CPU' in res.json
        assert 'GPU' in res.json
        assert 'Iterations' in res.json
        assert 'Memory' in res.json
        assert 'Training_Duration' in res.json        
        assert res.json['Progress'] == 1.0
        assert res.json['Status'] == 'Finished'
        
        for type_ in ['global-results', 'end-results']:
            res = client.get(
                f'/models/{model_id}/training/{training_session_id}/results?type={type_}',
                headers={'Authorization': user_token}                        
            )
            
            assert res.status_code == 200    
            assert res.json != {}

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-completed'}
        )


    wait_for_training_completed()

    
@pytest.mark.parametrize("deployment", ["export", "serving"])    
@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow(client, deployment, mixpanel_mock, user_token, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings)

    user_email = 'anton.k@perceptilabs.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_info(client, model_id, dataset_settings, network, user_email)    
    assert_previews(client, model_id, dataset_settings, network, user_email)

    assert_layer_code(client, model_id, network, user_email)
    
    assert_training(
        client, mixpanel_mock, user_token, model_id,
        network, dataset_settings, training_settings, training_session_id, user_email
    )

    res = client.post(
        f'/inference/testing',
        json={
            'modelsInfo': {
                model_id: {
                    'layers': network,
                    'model_name': 'MyModel',
                    'training_session_id': training_session_id,
                    'datasetSettings': dataset_settings
                }
            },
            'tests': ['confusion_matrix'],
            'userEmail': user_email
        },
        headers={'Authorization': user_token}                
    )
    assert res.status_code == 200
    testing_session_id = res.json

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing():
        res = client.get(
            f'/inference/testing/{testing_session_id}/status',
            headers={'Authorization': user_token}        
        )
        
        assert res.status_code == 200
        assert res.json['status'] == 'Completed'

        res = client.get(
            f'/inference/testing/{testing_session_id}/results',
            headers={'Authorization': user_token}
        )
        
        assert res.status_code == 200    
        assert res.json['confusion_matrix'] != {}
        
        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'testing-completed'}
        )
        

    wait_for_testing()

    if deployment == 'export':
        assert_export(
            client, mixpanel_mock, user_token, dataset_settings, network, user_email, model_id, training_session_id, tmp_path)
    elif deployment == 'serving':
        assert_serving(
            client, mixpanel_mock, user_token, dataset_settings, network, user_email, model_id, training_session_id)
        

@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_multi_input_modeling_flow(client, mixpanel_mock, user_token, tmp_path, dataset_settings, training_settings):
    dataset_settings["featureSpecs"]["x2"]["iotype"] = "input"  # Enable more inputs
    assert_data(client, dataset_settings)

    network = assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings)    
    user_email = 'anton.k@perceptilabs.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_training(
        client, mixpanel_mock, user_token, model_id, network,
        dataset_settings, training_settings, training_session_id, user_email
    )
    
    assert_export(
        client, mixpanel_mock, user_token,
        dataset_settings, network, user_email, model_id, training_session_id, tmp_path
    )


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow_stop_training(client, tmp_path, dataset_settings, training_settings, mixpanel_mock, user_token):
    training_settings["Epochs"] = 500  # Ensure we run for a while...

    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings)
    user_email = 'anton.k@perceptilabs.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    res = client.post(
        f'/models/{model_id}/training/{training_session_id}',
        json={
            'network': network,
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}        
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_started():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
            headers={'Authorization': user_token}            
        )
        assert res.status_code == 200
        assert res.json['Progress'] > 0

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-started'}
        )
        

    wait_for_training_started()

    # Stop training
    res = client.put(
        f'/models/{model_id}/training/{training_session_id}/stop',
        headers={'Authorization': user_token}        
    )
    
    assert res.status_code == 200
    assert res.json == 'success'

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_stopped():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
            headers={'Authorization': user_token}
        )
        
        assert res.status_code == 200
        assert res.json['Progress'] < 1.0
        assert res.json['Status'] == 'Stopped'

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-stopped'}
        )
        
    wait_for_training_stopped()    


def test_endpoint_error_handling_automatically_adds_fields(client, user_token):
    res = client.get('/bla', headers={'Authorization': user_token})  # Ping an endpoint that doesn't exist...
    assert res.status_code == 200
    assert res.json['error']['message']
    assert res.json['error']['details']


def test_type_inference(client, user_token, mixpanel_mock):
    res = client.get(
        '/datasets/type_inference?dataset_id=123',        
        headers={'Authorization': user_token}
    )
    assert res.status_code == 200

    assert res.json == {
        'x1': [['categorical', 'numerical'], 0],
        'x2': [['categorical', 'numerical'], 0],        
        'y1': [['categorical', 'text'], 0]
    }

    assert has_been_called_with(
        mixpanel_mock.track,
        kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'data-selected'}
    )
    
    
@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)    
def test_preprocessing_error(monkeypatch, client, tmp_path, dataset_settings, training_settings):
    error_message = 'some-random-error-message'
    
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)
    
    from perceptilabs.data.base import DataLoader    
    monkeypatch.setattr(DataLoader, 'compute_metadata', fake_call, raising=True)
    
    res = client.put(
        '/datasets/preprocessing',
        json={'datasetSettings': dataset_settings},
        headers={'Authorization': user_token}        
    )
    assert res.status_code == 200
    assert 'preprocessingSessionId' in res.json

    preprocessing_session_id = res.json['preprocessingSessionId']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_data_error():
        res = client.get(
            f"/datasets/preprocessing/{preprocessing_session_id}",
            headers={'Authorization': user_token}            
        )
        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']
        
    wait_for_data_error()        
    

@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)    
def test_training_error(monkeypatch, client, tmp_path, dataset_settings, training_settings, mixpanel_mock, user_token):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings)
    
    user_email = 'anton.k@perceptilabs.com'  # TODO: can i remove user_email arg from all tests?
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    res = client.post(
        f'/models/{model_id}/training/{training_session_id}',
        json={
            'network': network,
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
            'userEmail': user_email
        },
        headers={'Authorization': user_token}        
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}


    error_message = 'some-random-error-message'
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_error():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
            headers={'Authorization': user_token}            
        )
        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']         
        
        
    from perceptilabs.trainer.model import TrainingModel
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)
    
    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)
        
    wait_for_training_error()


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)    
def test_testing_error(monkeypatch, client, tmp_path, dataset_settings, training_settings, mixpanel_mock, user_token):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, mixpanel_mock, user_token, dataset_settings)
    
    user_email = 'anton.k@perceptilabs.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_training(
        client, mixpanel_mock, user_token, model_id,
        network, dataset_settings, training_settings, training_session_id, user_email)


    res = client.post(
        f'/inference/testing',
        json={
            'modelsInfo': {
                model_id: {
                    'layers': network,
                    'model_name': 'MyModel',
                    'training_session_id': training_session_id,
                    'datasetSettings': dataset_settings
                }
            },
            'tests': ['confusion_matrix'],
            'userEmail': user_email
        },
        headers={'Authorization': user_token}        
    )
    assert res.status_code == 200
    testing_session_id = res.json

    error_message = 'some-random-error-message'
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing_error():
        res = client.get(
            f'/inference/testing/{testing_session_id}/status',
            headers={'Authorization': user_token}                        
        )

        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']                 
        
    from perceptilabs.trainer.model import TrainingModel
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)
    
    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)
    
    wait_for_testing_error()
    

def test_set_user(client, mixpanel_mock, user_token):
    res = client.post('/user', headers={'Authorization': user_token})    
    assert res.status_code == 200
    assert res.json == "User has been set to anton.k@perceptilabs.com"

    assert has_been_called_with(
        mixpanel_mock.track,
        kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'user_email_set'}
    )
    
    
def test_get_version(client):
    import sys
    import tensorflow as tf

    response = client.get("/version")
    assert response.status_code == 200
    assert response.json == {
        'perceptilabs': 'development', 'python': sys.version, 'tensorflow': tf.__version__}
    
