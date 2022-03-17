import os
import pytest
import numpy as np
import pandas as pd
from mixpanel import Mixpanel
from unittest.mock import MagicMock
from retrying import retry

from celery.contrib.pytest import (
    celery_worker, celery_app, celery_config,
    celery_parameters, celery_enable_logging,
    use_celery_app_trap, celery_includes,
    celery_worker_pool, celery_worker_parameters
)

from perceptilabs.rygg import RyggWrapper
from perceptilabs.caching.utils import DictCache
from perceptilabs.api.base import create_app
from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor
import perceptilabs.settings as settings


@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'threads'


@pytest.fixture(scope='function', autouse=True)
def mixpanel_mock(monkeypatch):
    fn_track = MagicMock()
    fn_set_once = MagicMock()
    fn_set = MagicMock()

    monkeypatch.setattr(Mixpanel, 'track', fn_track, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set_once', fn_set_once, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set', fn_set, raising=True)

    return Mixpanel


@pytest.fixture(scope='function', autouse=True)
def rygg_mock(monkeypatch, tmp_path):
    df = pd.DataFrame({
        'x1': np.random.random((100,)).tolist(),
        'x2': np.random.random((100,)).tolist(),
        'y1': ['a', 'b', 'c', 'd']*25
    })
    location1 = os.path.join(tmp_path, 'data1.csv')
    df.to_csv(location1, index=False)

    df = pd.DataFrame({
        'a1': np.random.random((100,)).tolist(),
        'b2': np.random.random((100,)).tolist(),
        'c1': ['a', 'b', 'c', 'd']*25
    })
    location2 = os.path.join(tmp_path, 'data2.csv')
    df.to_csv(location2, index=False)

    def get_dataset(self, call_context, dataset_id):
        if str(dataset_id) == '123':
            location = location1
        elif str(dataset_id) == '456':
            location = location2
        else:
            raise ValueError(f"No dataset with ID {dataset_id}")

        response = {
            'location': location,
            'name': 'MyDataset',
            'is_perceptilabs_sourced': True
        }
        return response

    def get_tf_hub_cache_dir(self, call_context):
        response = {
            "tf_hub_cache_dir": str(tmp_path.stem)
        }
        return response

    from perceptilabs.rygg import RyggWrapper
    monkeypatch.setattr(RyggWrapper, 'get_dataset', get_dataset)
    monkeypatch.setattr(RyggWrapper, 'get_tf_hub_cache_dir', get_tf_hub_cache_dir)
    models = {}

    # TODO: in frontend, we must always update model in rygg before we tell kernel smth.. which endpoints are affected?

    def create_model(self, call_context, dataset_id, model_name, location=None):
        model_id = str(len(models) + 100)
        meta = {
            'location': location or os.path.join(tmp_path, model_name),
            'model_id': model_id,
        }
        models[model_id] = {
            'meta': meta,
            'model_json': {}
        }
        return meta

    def get_model(self, call_context, model_id):
        return models.get(model_id, {}).get('meta', {})

    def save_model_json(self, call_context, model_id, model):
        #import pdb; pdb.set_trace()
        models[model_id]['model_json'] = model

    def load_model_json(self, call_context, model_id):
        return models.get(model_id, {}).get('model_json', {})


    monkeypatch.setattr(RyggWrapper, 'get_dataset', get_dataset)
    monkeypatch.setattr(RyggWrapper, 'create_model', create_model)
    monkeypatch.setattr(RyggWrapper, 'get_model', get_model)
    monkeypatch.setattr(RyggWrapper, 'save_model_json', save_model_json)
    monkeypatch.setattr(RyggWrapper, 'load_model_json', load_model_json)

class MockAuth():
    def __init__(self, app, **kwargs):
        self.app = app

    def __call__(self, environ, start_response):
        environ['user'] = 'the unique user id'
        environ['auth_token'] = {
            'this': 'is the decoded token',
            'email': 'anton.k@perceptilabs.com',
        }
        environ['auth_token_raw'] = 'this is the raw token'
        return self.app(environ, start_response)

def mock_auth(monkeypatch):
    import perceptilabs.api.base as app
    import perceptilabs.auth

    # monkeypatch.setattr(auth, 'AUTH_ISSUER', 'unittest', raising=True)
    def foo(*args, **kwargs):
        return MockAuth(*args, **kwargs)
    monkeypatch.setattr(app, 'jwt_middleware', foo)



@pytest.fixture(scope='function')
def client(monkeypatch, request, celery_worker):
    mock_auth(monkeypatch)
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


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
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


def assert_export(client, mixpanel_mock, dataset_settings, model_id, training_session_id, tmp_path, graph_settings=None):
    res = client.put(
        f'/models/{model_id}/export?training_session_id={training_session_id}',
        json={
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
            'graphSettings': graph_settings
        },
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

def assert_serving(mode, client, mixpanel_mock, dataset_settings, model_id, training_session_id, graph_settings=None):

    if mode == 'zip':
        serving_settings = {
            'mode': 'zip',
            'exportSettings': {
                'Type': 'Standard',
            },
            'ExcludePreProcessing': False,
            'ExcludePostProcessing': False,
        }
    else:
        serving_settings = {
            'mode': 'gradio',
            'ExcludePreProcessing': False,
            'ExcludePostProcessing': False,
        }        
    
    res = client.post(
        f'/inference/serving/{model_id}?training_session_id={training_session_id}',
        json={
            'settings': serving_settings,
            'datasetSettings': dataset_settings,
            'modelName': 'my-model',
            'graphSettings': graph_settings,
            'ttl': 10
        },
    )
    assert res.status_code == 200
    serving_session_id = res.json


    def assert_download_model_zip(url):
        import requests
        import zipfile
        import io

        # TODO: cleanup
        # url = 'https://golang.org/dl/go1.17.3.windows-amd64.zip'  # TODO: remove 
        #url = "return (resp.text, resp.status_code, resp.headers.items())"
        #url = f'localhost:5001/inference/serving/{serving_session_id}/proxy'
        #res = requests.get(url, stream=True, headers={'Authorization': user_token})
        res = client.get(url)

        file_like = io.BytesIO(res.data)
        zipfile = zipfile.ZipFile(file_like)
        files = zipfile.namelist()

        assert 'saved_model.pb' in files
        assert 'variables/' in files
        assert 'assets/' in files
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_serving_up():
        res = client.get(
            f"/inference/serving/{serving_session_id}/status",
        )
        assert res.status_code == 200
        assert 'url' in res.json

        if mode == 'zip':
            assert_download_model_zip(res.json['url'])            
        
        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'model-exported'}
        )

    wait_for_serving_up()

    res = client.post(
        f"/inference/serving/{serving_session_id}/stop",
    )
    assert res.status_code == 200

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_serving_down():
        res = client.get(
            f"/inference/serving/{serving_session_id}/status",
        )
        assert res.status_code == 200
    
    wait_for_serving_down()            


def assert_data(client, dataset_settings):
    # Start preprocessing the dataset
    res = client.put(
        '/datasets/preprocessing',
        json={'datasetSettings': dataset_settings},
    )
    assert res.status_code == 200
    assert 'preprocessingSessionId' in res.json

    preprocessing_session_id = res.json['preprocessingSessionId']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_data():
        res = client.get(
            f"/datasets/preprocessing/{preprocessing_session_id}",
        )
        assert res.status_code == 200
        assert res.json == {'is_complete': True, 'message': "Build status: 'complete'", 'error': None}

    wait_for_data()


def assert_model_recommendation(client, mixpanel_mock, dataset_settings):
    # Get a model recommendation
    res = client.post(
        '/models/recommendations',
        json={
            'projectId': 100,
            'datasetId': 123, # TODO: as param
            'modelName': 'MyModel', # TODO: as param
            'datasetSettings': dataset_settings
        },
    )
    assert res.status_code == 200
    assert mixpanel_mock.track.call_args[1]['distinct_id'] == 'anton.k@perceptilabs.com'
    assert mixpanel_mock.track.call_args[1]['event_name'] == 'model-recommended'

    model_id = res.json['model_id']
    graph_settings = res.json['graph_settings']
    return model_id, graph_settings


def assert_info(client, model_id, dataset_settings, graph_settings=None):
    res = client.post(
        f'/models/{model_id}/layers/info',
        json={
            'datasetSettings': dataset_settings,
            'graphSettings': graph_settings
        },
    )

    for layer_id, layer_info in res.json.items():
        assert 'inShape' in layer_info
        assert 'outShape' in layer_info

    for layer_id in ['0', '1', '2']:
        res = client.post(
            f'/models/{model_id}/layers/{layer_id}/info',
            json={
                'datasetSettings': dataset_settings,
            },
        )
        assert 'inShape' in res.json
        assert 'outShape' in res.json


def assert_previews(client, model_id, dataset_settings, graph_settings=None):
    res = client.post(
        f'/models/{model_id}/layers/previews',
        json={
            'datasetSettings': dataset_settings,
            'graphSettings': graph_settings
        },
    )

    assert res.status_code == 200
    assert res.json['outputDims']['0'] == {'Dim': '1', 'Error': None}
    assert res.json['outputDims']['1'] == {'Dim': '4', 'Error': None}
    assert res.json['outputDims']['2'] == {'Dim': '4', 'Error': None}

    assert 'series' in res.json['previews']['0']
    assert 'xLength' in res.json['previews']['0']

    assert 'series' in res.json['previews']['1']
    assert 'xLength' in res.json['previews']['1']

    assert 'series' in res.json['previews']['2']
    assert 'xLength' in res.json['previews']['2']


def assert_layer_code(client, model_id, graph_settings=None):
    res = client.post(
        f'/models/{model_id}/layers/1/code',
        json={'graphSettings': graph_settings},
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


def assert_training(client, mixpanel_mock, model_id, dataset_settings, training_settings, graph_settings=None):
    res = client.post(
        f'/models/{model_id}/training',
        json={
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'graphSettings': graph_settings,
            'loadCheckpoint': False,
        },
    )
    assert res.status_code == 200
    assert res.json['content'] == 'core started'
    assert res.json['training_session_id']
    training_session_id = res.json['training_session_id']

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
            )

            assert res.status_code == 200
            assert res.json != {}

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-completed'}
        )


    wait_for_training_completed()
    return training_session_id


def assert_testing(client, mixpanel_mock, model_id, training_session_id, dataset_settings):
    res = client.post(
        f'/inference/testing',
        json={
            'modelsInfo': {
                model_id: {
                    'model_name': 'MyModel',
                    'training_session_id': training_session_id,
                    'datasetSettings': dataset_settings
                }
            },
            'tests': ['confusion_matrix'],
        },
    )
    assert res.status_code == 200
    testing_session_id = res.json

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing():
        res = client.get(
            f'/inference/testing/{testing_session_id}/status',
        )

        assert res.status_code == 200
        assert res.json['status'] == 'Completed'

        res = client.get(
            f'/inference/testing/{testing_session_id}/results',
        )

        assert res.status_code == 200
        assert res.json['confusion_matrix'] != {}

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'testing-completed'}
        )

    wait_for_testing()
    return testing_session_id

    
@pytest.mark.parametrize("deployment", ["export", "serve_gradio", "serve_zip"])    
@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow_basic(client, deployment, mixpanel_mock, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    model_id, _ = assert_model_recommendation(
        client, mixpanel_mock, dataset_settings)

    assert_info(client, model_id, dataset_settings)
    assert_previews(client, model_id, dataset_settings)
    assert_layer_code(client, model_id)

    training_session_id = assert_training(
        client, mixpanel_mock, model_id,
        dataset_settings, training_settings
    )

    assert_testing(client, mixpanel_mock, model_id, training_session_id, dataset_settings)

    if deployment == 'export':
        assert_export(client, mixpanel_mock, dataset_settings, model_id, training_session_id, tmp_path)
    elif deployment == 'serve_gradio':
        assert_serving('gradio', client, mixpanel_mock, dataset_settings, model_id, training_session_id)
    elif deployment == 'serve_zip':
        assert_serving('zip', client, mixpanel_mock, dataset_settings, model_id, training_session_id)

        
@pytest.mark.parametrize("deployment", ["export", "serve_gradio"])
def test_modeling_flow_with_graph_settings_in_payload(client, deployment, mixpanel_mock, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    
    model_id, graph_settings = assert_model_recommendation(
        client, mixpanel_mock, dataset_settings)

    assert_info(client, model_id, dataset_settings, graph_settings=graph_settings)
    assert_previews(client, model_id, dataset_settings, graph_settings=graph_settings)
    assert_layer_code(client, model_id, graph_settings=graph_settings)

    training_session_id = assert_training(
        client, mixpanel_mock, model_id,
        dataset_settings, training_settings, graph_settings=graph_settings
    )

    assert_testing(client, mixpanel_mock, model_id, training_session_id, dataset_settings)

    if deployment == 'export':
        assert_export(
            client, mixpanel_mock, dataset_settings, model_id, training_session_id, tmp_path, graph_settings=graph_settings)
    elif deployment == 'serve_gradio':
        assert_serving(
            'gradio', client, mixpanel_mock, dataset_settings, model_id, training_session_id, graph_settings=graph_settings)
        
        
@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_multi_input_modeling_flow(client, mixpanel_mock, tmp_path, dataset_settings, training_settings):
    dataset_settings["featureSpecs"]["x2"]["iotype"] = "input"  # Enable more inputs
    assert_data(client, dataset_settings)

    model_id, _ = assert_model_recommendation(client, mixpanel_mock, dataset_settings)

    training_session_id = assert_training(
        client, mixpanel_mock, model_id,
        dataset_settings, training_settings
    )

    assert_export(
        client, mixpanel_mock,
        dataset_settings, model_id, training_session_id, tmp_path
    )


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow_stop_training(client, tmp_path, dataset_settings, training_settings, mixpanel_mock):
    training_settings["Epochs"] = 500  # Ensure we run for a while...

    assert_data(client, dataset_settings)
    model_id, _ = assert_model_recommendation(client, mixpanel_mock, dataset_settings)

    res = client.post(
        f'/models/{model_id}/training',
        json={
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
        },
    )
    assert res.status_code == 200
    assert res.json['content'] == 'core started'
    assert res.json['training_session_id']
    training_session_id = res.json['training_session_id']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_started():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
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
    )

    assert res.status_code == 200
    assert res.json == 'success'

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_stopped():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
        )

        assert res.status_code == 200
        assert res.json['Progress'] < 1.0
        assert res.json['Status'] == 'Stopped'

        assert has_been_called_with(
            mixpanel_mock.track,
            kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'training-stopped'}
        )

    wait_for_training_stopped()


def test_endpoint_error_handling_automatically_adds_fields(client):
    res = client.get('/bla')  # Ping an endpoint that doesn't exist...
    assert res.status_code == 200
    assert res.json['error']['message']
    assert res.json['error']['details']


def test_type_inference(client, mixpanel_mock):
    res = client.get(
        '/datasets/type_inference?dataset_id=123',
    )
    assert res.status_code == 200

    assert res.json == {
        'x1': [['categorical', 'numerical'], 1],
        'x2': [['categorical', 'numerical'], 1],
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
    )
    assert res.status_code == 200
    assert 'preprocessingSessionId' in res.json

    preprocessing_session_id = res.json['preprocessingSessionId']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_data_error():
        res = client.get(
            f"/datasets/preprocessing/{preprocessing_session_id}",
        )

        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']

    wait_for_data_error()


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_training_error(monkeypatch, client, tmp_path, dataset_settings, training_settings, mixpanel_mock):
    assert_data(client, dataset_settings)
    model_id, _ = assert_model_recommendation(client, mixpanel_mock, dataset_settings)

    res = client.post(
        f'/models/{model_id}/training',
        json={
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
        },
    )
    assert res.status_code == 200
    assert res.json['content'] == 'core started'
    assert res.json['training_session_id']
    training_session_id = res.json['training_session_id']

    error_message = 'some-random-error-message'

    @retry(stop_max_attempt_number=20, wait_fixed=1000)
    def wait_for_training_error():
        res = client.get(
            f'/models/{model_id}/training/{training_session_id}/status',
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
def test_testing_error(monkeypatch, client, tmp_path, dataset_settings, training_settings, mixpanel_mock):
    assert_data(client, dataset_settings)
    model_id, _ = assert_model_recommendation(client, mixpanel_mock, dataset_settings)

    training_session_id = assert_training(
        client, mixpanel_mock, model_id,
        dataset_settings, training_settings
    )

    res = client.post(
        f'/inference/testing',
        json={
            'modelsInfo': {
                model_id: {
                    'model_name': 'MyModel',
                    'training_session_id': training_session_id,
                    'datasetSettings': dataset_settings
                }
            },
            'tests': ['confusion_matrix'],
        },
    )
    assert res.status_code == 200
    testing_session_id = res.json

    error_message = 'some-random-error-message'

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing_error():
        res = client.get(
            f'/inference/testing/{testing_session_id}/status',
        )

        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']

    from perceptilabs.trainer.model import TrainingModel
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)

    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)

    wait_for_testing_error()


def test_set_user(client, mixpanel_mock):
    res = client.post('/user')
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


#@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_sharing_flow(client, mixpanel_mock, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    model_id, _ = assert_model_recommendation(client, mixpanel_mock, dataset_settings)

    assert_info(client, model_id, dataset_settings)
    assert_previews(client, model_id, dataset_settings)

    assert_layer_code(client, model_id)

    training_session_id = assert_training(
        client, mixpanel_mock, model_id,
        dataset_settings, training_settings
    )

    res = client.put(
        f'/models/{model_id}/export?training_session_id={training_session_id}',
        json={
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'exportSettings': {
                'Location': str(tmp_path),
                'name': 'my-model',
                'Type': 'Archive',
            }
        },
    )
    archive_path = os.path.join(tmp_path, f'model_{model_id}.zip')
    assert os.path.isfile(archive_path)


    res = client.post(
        f'/models/import',
        json={
            'archiveFilePath': archive_path,
            'projectId': '10',
            'datasetId': '456',
            'modelName': 'my-new-model',
            'modelFilePath': tmp_path,
        },
    )
    
    assert has_been_called_with(
        mixpanel_mock.track,
        kwargs={'distinct_id': 'anton.k@perceptilabs.com', 'event_name': 'model-imported'}
    )
    assert_training(
        client, mixpanel_mock, res.json['modelId'],
        res.json['datasetSettings'], res.json['trainingSettings']   # TODO: these should NOT be returned. We should instead return the dataset settings ID (hash? or model id?) and training session ID (model id)... What about frontend settings? Leave for now?
    )

@pytest.fixture(scope='function', autouse=True)
def client_with_no_auth():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_non_auth(client_with_no_auth):
    res = client_with_no_auth.get('/version')
    assert res.status_code == 200

    res = client_with_no_auth.get('/healthy')
    assert res.status_code == 200
