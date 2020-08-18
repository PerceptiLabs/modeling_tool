import tensorflow as tf
import numpy as np
import pytest

from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.messaging.simple import SimpleMessagingFactory
from perceptilabs.api.experiment import Experiment

@pytest.fixture
def message_factory():
    message_factory = SimpleMessagingFactory()
    return message_factory

@pytest.fixture
def producer(message_factory):
    message_producer = message_factory.make_producer('generic-experiment')
    return message_producer

@pytest.fixture
def consumer(message_factory):
    message_consumer = message_factory.make_consumer('generic-experiment')
    return message_consumer

def test_experiment_log_metric(producer, consumer):
    # Declare experiment
    experiment_name = 'Test-1'
    train_loss_input = np.random.normal(size=5)
    test_loss_input = np.random.normal(size=1)

    ex = Experiment(experiment_name=experiment_name, producer=producer)

    # Send data
    for index, loss in enumerate(train_loss_input):
        ex.log_metric('Train Loss', loss, index)

    ex.log_metric('Test Loss', test_loss_input[0], 0)

    # Receive data and assert
    raw_messages = consumer.get_messages()
    train_loss_rec = []
    test_loss_rec = []

    for raw_message in raw_messages:
        message = deserialize(raw_message)

        if message['name'] == 'Train Loss':
            train_loss_rec.append(message['metric'])
        elif message['name'] == 'Test Loss':
            test_loss_rec.append(message['metric'])

    assert len(train_loss_input) == len(train_loss_rec)
    assert len(test_loss_input) == len(test_loss_rec)
    assert np.isclose(train_loss_input, train_loss_rec).all()
    assert np.isclose(test_loss_input, test_loss_rec).all()

def test_experiment_log_hyperparameters(producer, consumer):
    # Create hyperparameters and declare experiment
    experiment_name = 'Test-2'
    hyper_params = {
        'learning_rate': 0.01,
        'batch_size': 10,
        'steps': 10
    }

    # Send data
    ex = Experiment(experiment_name=experiment_name, producer=producer)
    ex.log_hyperparameters(hyper_params)

    # Receive data and assert
    raw_message = consumer.get_messages()
    message = deserialize(raw_message[0])

    assert message['experiment_name'] == experiment_name
    assert message['category'] == 'Hyperparameters'
    assert message['hyper_params']['learning_rate'] == hyper_params['learning_rate']
    assert message['hyper_params']['batch_size'] == hyper_params['batch_size']
    assert message['hyper_params']['steps'] == hyper_params['steps']

def test_experiment_log_ndarray_metrics(producer, consumer):
    # Declare experiment
    experiment_name = 'Test-3'
    gradient = np.array([[1,2,3], [4,5,6]])
    bias = np.array([[2,4,6], [4,6,8]])

    # Send data
    ex = Experiment(experiment_name=experiment_name, producer=producer)
    ex.log_metric('Gradient', gradient, 0)
    ex.log_metric('Bias', bias, 0)

    # Receive data and assert
    raw_message = consumer.get_messages()
    message_grad = deserialize(raw_message[0])
    message_bias = deserialize(raw_message[1])

    assert message_grad['experiment_name'] == experiment_name
    assert message_bias['experiment_name'] == experiment_name

    assert message_grad['name'] == 'Gradient'
    assert message_bias['name'] == 'Bias'

    assert np.isclose(gradient, message_grad['metric']).all()
    assert np.isclose(bias, message_bias['metric']).all()