import tensorflow as tf
import numpy as np
import pytest
import random

from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.api.data_container import DataContainer

@pytest.fixture
def datacontainer():
    dc = DataContainer()

    return dc

def raw_message(exp_name, name, metric, step):
    r_message = {
        'experiment_name': exp_name,
        'category': 'Metrics',
        'name': name,
        'metric': metric,
        'step': step
    }
    
    return r_message

def test_data_container_hyperparameters(datacontainer):
    # Initialize hyperparameters to feed into DataContainer
    hyper_params = {
        'learning_rate': 0.01,
        'batch_size': 10,
        'steps': 10
    }

    raw_message = {
        'experiment_name': 'Test1',
        'category': 'Hyperparameters',
        'hyper_params': hyper_params
    }

    message = serialize(raw_message)
    datacontainer.process_message(message)

    # Grab stored hyperparameters out of DataContainer and assert
    assert datacontainer.get_hyperparameter('Test1', 'learning_rate') == 0.01
    assert datacontainer.get_hyperparameter('Test1', 'batch_size') == 10
    assert datacontainer.get_hyperparameter('Test1', 'steps') == 10
    assert set(datacontainer.get_hyperparameter_names('Test1')) == set(['learning_rate', 'batch_size', 'steps'])

def test_data_container_metric(datacontainer):
    # Initialize metrics to feed into DataContainer
    train_loss = []
    test_loss = np.empty(10)
    test_loss.fill(np.nan)
    test_loss[0] = np.random.uniform(0, 1)

    # Send data
    for i in range(5):
        train_loss.append(np.random.uniform(0,1))
        r_message = raw_message('Test2', 'Train Loss', train_loss[i*2], i*2)
        train_loss.append(np.nan)

        message = serialize(r_message)
        datacontainer.process_message(message)

    r_message = raw_message('Test2', 'Test Loss', test_loss[0], 0)
    message = serialize(r_message)
    datacontainer.process_message(message)

    # Grab stored metric out of DataContainer and assert
    assert len(datacontainer.get_metric('Test2', 'Train Loss', start=0)) == 9
    assert len(datacontainer.get_metric('Test2', 'Train Loss', start=1, end=5)) == 5
    assert len(datacontainer.get_metric('Test2', 'Train Loss', end=-2)) == 2
    assert len(datacontainer.get_metric('Test2', 'Test Loss', start=0, end=9)) == 10
    assert len(datacontainer.get_metric('Test2', 'Test Loss', end=-4)) == 4

    assert np.isclose(datacontainer.get_metric('Test2', 'Train Loss', start=0), train_loss[:-1], equal_nan=True).all()
    assert np.isclose(datacontainer.get_metric('Test2', 'Train Loss', end=-5), train_loss[-6:-1], equal_nan=True).all()
    assert np.isclose(datacontainer.get_metric('Test2', 'Test Loss', start = 0, end=9), test_loss, equal_nan=True).all()
    assert np.isclose(datacontainer.get_metric('Test2', 'Test Loss', end=-5), test_loss[:5], equal_nan=True).all()

def test_data_container_reset(datacontainer):
    train_loss = np.random.normal(size=5)
    test_loss = np.empty(5)
    test_loss.fill(np.nan)
    test_loss[0] = np.random.uniform(0, 1)

    # Send data
    for i in range(5):
        r_message = raw_message('Test3', 'Train Loss', train_loss[i], i)

        message = serialize(r_message)
        datacontainer.process_message(message)

    r_message = raw_message('Test3', 'Test Loss', test_loss[0], 0)
    message = serialize(r_message)
    datacontainer.process_message(message)

    # Delete experiment
    datacontainer._delete_experiment('Test3')
    experiment_names = datacontainer.get_experiment_names()
    
    assert 'Test3' not in experiment_names