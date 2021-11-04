import os
import pytest
from retrying import retry

from celery.contrib.pytest import (
    celery_worker, celery_app, celery_config,
    celery_parameters, celery_enable_logging,
    use_celery_app_trap, celery_includes,
    celery_worker_pool, celery_worker_parameters
)


from perceptilabs.caching.utils import DictCache
from perceptilabs.endpoints.base import create_app
from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor
import perceptilabs.settings as settings


def make_session_id(string):
    import base64    
    return base64.urlsafe_b64encode(string.encode()).decode()


# TODO: session IDs [both training and testing] should be created in the Kernel... As a hack, just aask for the checkpoint directory on "start training" and "start testing", then the frontend can keep track of the returned session IDs.


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
        "filePath": "perceptilabs/endpoints/test_data.csv",
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


def assert_export(client, dataset_settings, network, user_email, model_id, training_session_id, tmp_path):
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
                'Quantized': False
            },
            'userEmail': user_email
        }
    )
    expected_path = os.path.join(tmp_path, 'my-model')
    
    assert res.status_code == 200
    assert res.json == f"Model exported to '{expected_path}'"

    assert set(os.listdir(expected_path)) == set([
        'saved_model.pb', 'variables', 'keras_metadata.pb', 'assets'])


def assert_serving(client, dataset_settings, network, user_email, model_id, training_session_id):
    res = client.post(
        f'/models/{model_id}/serve?training_session_id={training_session_id}', 
        json={
            'type': 'gradio',
            'network': network,
            'datasetSettings': dataset_settings,
            'modelName': 'my-model',
            'userEmail': user_email
        }
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
        res = client.get(f"/models/serving/{serving_session_id}/status")
        assert res.status_code == 200
        assert 'url' in res.json
        assert not has_expired(res.json['last_update'])

    wait_for_serving_up()                    

    res = client.post(f"/models/serving/{serving_session_id}/stop")
    assert res.status_code == 200
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_serving_down():
        res = client.get(f"/models/serving/{serving_session_id}/status")
        assert res.status_code == 200
        assert has_expired(res.json['last_update'])        
    
    wait_for_serving_down()            

    
def assert_data(client, dataset_settings):
    # Start preprocessing the dataset
    res = client.put('/data', json={'datasetSettings': dataset_settings})
    assert res.status_code == 200
    assert 'datasetHash' in res.json

    dataset_hash = res.json['datasetHash']

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_data():
        res = client.get(f"/data?dataset_hash={dataset_hash}")
        assert res.status_code == 200    
        assert res.json == {'is_complete': True, 'message': "Build status: 'complete'"}
        
    wait_for_data()        


def assert_model_recommendation(client, dataset_settings):
    # Get a model recommendation
    res = client.post('/model_recommendations', json={'datasetSettings': dataset_settings})    
    assert res.status_code == 200        
    network = res.json
    return network


def assert_training(client, model_id, network, dataset_settings, training_settings, training_session_id, user_email):
    res = client.post(
        f'/models/{model_id}/training/{training_session_id}',
        json={
            'network': network,
            'datasetSettings': dataset_settings,
            'trainingSettings': training_settings,
            'loadCheckpoint': False,
            'userEmail': user_email
        }
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}
                    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training():
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
                f'/models/{model_id}/training/{training_session_id}/results?type={type_}')
            
            assert res.status_code == 200    
            assert res.json != {}

    wait_for_training()

    
@pytest.mark.parametrize("deployment", ["export", "serving"])    
@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow(client, deployment, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, dataset_settings)
    
    user_email = 'a@b.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_training(client, model_id, network, dataset_settings, training_settings, training_session_id, user_email)

    res = client.post(
        f'/models/testing',
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
        }
    )
    assert res.status_code == 200
    testing_session_id = res.json

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing():
        res = client.get(
            f'/models/testing/{testing_session_id}/status')
        
        assert res.status_code == 200
        assert res.json['status'] == 'Completed'

        res = client.get(
            f'/models/testing/{testing_session_id}/results')
        
        assert res.status_code == 200    
        assert res.json['confusion_matrix'] != {}

    wait_for_testing()

    if deployment == 'export':
        assert_export(
            client, dataset_settings, network, user_email, model_id, training_session_id, tmp_path)
    elif deployment == 'serving':
        assert_serving(
            client, dataset_settings, network, user_email, model_id, training_session_id)
        

@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_multi_input_modeling_flow(client, tmp_path, dataset_settings, training_settings):
    dataset_settings["featureSpecs"]["x2"]["iotype"] = "input"  # Enable more inputs
    assert_data(client, dataset_settings)

    network = assert_model_recommendation(client, dataset_settings)    
    user_email = 'a@b.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_training(client, model_id, network, dataset_settings, training_settings, training_session_id, user_email)
    
    assert_export(
        client, dataset_settings, network, user_email, model_id, training_session_id, tmp_path)


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)
def test_modeling_flow_stop_training(client, tmp_path, dataset_settings, training_settings):
    training_settings["Epochs"] = 500  # Ensure we run for a while...

    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, dataset_settings)
    user_email = 'a@b.com'
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
        }
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_started():
        res = client.get(f'/models/{model_id}/training/{training_session_id}/status')
        assert res.status_code == 200
        assert res.json['Progress'] > 0

    wait_for_training_started()

    # Stop training
    res = client.put(f'/models/{model_id}/training/{training_session_id}/stop')
    
    assert res.status_code == 200
    assert res.json == 'success'

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_stopped():
        res = client.get(f'/models/{model_id}/training/{training_session_id}/status')        
        assert res.status_code == 200
        assert res.json['Progress'] < 1.0
        assert res.json['Status'] == 'Stopped'
    
    wait_for_training_stopped()    


def test_endpoint_error_handling_automatically_adds_fields(client):
    res = client.get('/bla')  # Ping an endpoint that doesn't exist...
    assert res.status_code == 200
    assert res.json['error']['message']
    assert res.json['error']['details']


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)    
def test_training_error(monkeypatch, client, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, dataset_settings)
    
    user_email = 'a@b.com'
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
        }
    )
    assert res.status_code == 200
    assert res.json == {'content': 'core started'}


    error_message = 'some-random-error-message'
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_training_error():
        res = client.get(f'/models/{model_id}/training/{training_session_id}/status')
        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']         
        
        
    from perceptilabs.trainer.model import TrainingModel
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)
    
    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)
        
    wait_for_training_error()


@pytest.mark.parametrize("client", ["threaded", "celery"], indirect=True)    
def test_testing_error(monkeypatch, client, tmp_path, dataset_settings, training_settings):
    assert_data(client, dataset_settings)
    network = assert_model_recommendation(client, dataset_settings)
    
    user_email = 'a@b.com'
    model_id = '123'
    training_session_id = make_session_id(str(tmp_path))  # TODO: This should be generated by one of the endpoints....

    assert_training(client, model_id, network, dataset_settings, training_settings, training_session_id, user_email)


    res = client.post(
        f'/models/testing',
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
        }
    )
    assert res.status_code == 200
    testing_session_id = res.json

    error_message = 'some-random-error-message'
    
    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_testing_error():
        res = client.get(
            f'/models/testing/{testing_session_id}/status')

        assert res.status_code == 200
        assert res.json['error']['message']
        assert error_message in res.json['error']['details']                 
        
    from perceptilabs.trainer.model import TrainingModel
    def fake_call(*args, **kwargs):
        raise ValueError(error_message)
    
    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)
    
    wait_for_testing_error()


    
