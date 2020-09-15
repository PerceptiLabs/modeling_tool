import numpy as np
import pandas as pd
import pytest
import time

from perceptilabs.api.data_container import DataContainer
from perceptilabs.api.experiment import Experiment
from perceptilabs.aggregation import AggregationEngine
from perceptilabs.mainInterface import Interface
from perceptilabs.coreInterface import coreLogic
from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.messaging.simple import SimpleMessagingFactory
from perceptilabs.messaging import MessageProducer, MessageConsumer, MessagingFactory
from perceptilabs.issues import IssueHandler

import perceptilabs.aggregation.aggregates as aggs

@pytest.fixture
def message_factory():
    message_factory = SimpleMessagingFactory()
    return message_factory

@pytest.fixture
def producer(message_factory):
    message_producer = message_factory.make_producer('generic-experiment')
    return message_producer

@pytest.fixture
def experiment(producer):
    exp = Experiment(experiment_name='Test-1', producer=producer)
    return exp

@pytest.fixture
def core_interface(message_factory):
    cores=dict()
    dataDict=dict()
    checkpointDict=dict()
    lwDict=dict()
    issue_handler = IssueHandler()
    core_interface = Interface(cores, dataDict, checkpointDict, lwDict, issue_handler, message_factory=message_factory)

    return core_interface

def create_schedule_aggregations_request_experiment():
    reciever = 0000
    action = "scheduleAggregations"
    value = [
        {
            'result_name': 'get_identity',
            'aggregate_name': 'identity',
            'experiment_name': 'Test-1',
            'metric_names': ['Train Loss', 'Test Loss'],
            'start': 0,
            'end': 4,
            'aggregate_kwargs': {}
        }
    ]

    return {"reciever": reciever, "action":action, "value":value}

def create_get_aggregation_results_request_experiment():
    reciever = 0000
    action = "getAggregationResults"
    value = ['get_identity']

    return {"reciever": reciever, "action":action, "value":value}
    
def create_schedule_aggregations_request_basic():
    reciever = 0000
    action = "scheduleAggregations"
    value = [
        {
            'result_name': 'get_average',
            'aggregate_name': 'average',
            'experiment_name': 'Test-1',
            'metric_names': ['Train Loss', 'Test Loss'],
            'start': 0,
            'end': 4,
            'aggregate_kwargs': {}
        }
    ]

    return {"reciever": reciever, "action":action, "value":value}

def create_get_aggregation_results_request_basic():
    reciever = 0000
    action = "getAggregationResults"
    value = ['get_average']

    return {"reciever": reciever, "action":action, "value":value}

def create_schedule_aggregations_request_extensive():
    reciever = 0000
    action = "scheduleAggregations"
    value = [
        {
            'result_name': 'get_average',
            'aggregate_name': 'average',
            'experiment_name': 'Test-1',
            'metric_names': ['Train Loss', 'Test Loss'],
            'start': 0,
            'end': 4,
            'aggregate_kwargs': {}
        },
        {
            'result_name': 'get_max',
            'aggregate_name': 'max',
            'experiment_name': 'Test-1',
            'metric_names': ['Train Loss', 'Test Loss'],
            'start': 0,
            'end': 4,
            'aggregate_kwargs': {}
        },
        {
            'result_name': 'get_min',
            'aggregate_name': 'min',
            'experiment_name': 'Test-1',
            'metric_names': ['Train Loss', 'Test Loss'],
            'start': 0,
            'end': 4,
            'aggregate_kwargs': {}
        }
    ]

    return {"reciever": reciever, "action":action, "value":value}

def create_get_aggregation_results_request_extensive():
    reciever = 0000
    action = "getAggregationResults"
    value = ['get_average', 'get_max', 'get_min']

    return {"reciever": reciever, "action":action, "value":value}

def test_get_experiment_data(core_interface, experiment):
    train_loss_input = np.random.normal(size=5)
    test_loss_input = np.empty(5)
    test_loss_input.fill(np.nan)
    test_loss_input[0] = np.random.normal(size=1)

    # Send data
    for index, loss in enumerate(train_loss_input):
        experiment.log_metric('Train Loss', loss, index)

    experiment.log_metric('Test Loss', test_loss_input[0], 0)

    time.sleep(2.5)

    # Schedule Aggregations
    request_schedule = create_schedule_aggregations_request_experiment()
    actual, _ = core_interface.create_response(request_schedule)

    # Get Aggregrations
    request_aggregations = create_get_aggregation_results_request_experiment()
    actual, _ = core_interface.create_response(request_aggregations)

    train_identity, test_identity = actual['get_identity']

    assert np.isclose(train_loss_input, train_identity, equal_nan=True).all()
    assert np.isclose(test_loss_input, test_identity, equal_nan=True).all()

def test_get_aggregations_results_basic(core_interface, experiment):
    train_loss_input = np.random.normal(size=5)
    test_loss_input = np.empty(5)
    test_loss_input.fill(np.nan)
    test_loss_input[0] = np.random.normal(size=1)

    expected = np.nanmean([train_loss_input, test_loss_input], axis=0)

    # Send data
    for index, loss in enumerate(train_loss_input):
        experiment.log_metric('Train Loss', loss, index)

    experiment.log_metric('Test Loss', test_loss_input[0], 0)

    time.sleep(2.5)

    # Schedule Aggregations
    request_schedule = create_schedule_aggregations_request_basic()
    actual, _ = core_interface.create_response(request_schedule)

    # Get Aggregrations
    request_aggregations = create_get_aggregation_results_request_basic()
    actual, _ = core_interface.create_response(request_aggregations)

    assert np.isclose(actual['get_average'], expected, equal_nan=True).all()  

def test_get_aggregations_results_extensive(core_interface, experiment):
    train_loss_input = np.random.normal(size=5)
    test_loss_input = np.empty(5)
    test_loss_input.fill(np.nan)
    test_loss_input[0] = np.random.normal(size=1)
    
    expected_mean = np.nanmean([train_loss_input, test_loss_input], axis=0)
    expected_max = np.nanmax([train_loss_input, test_loss_input], axis=0)
    expected_min = np.nanmin([train_loss_input, test_loss_input], axis=0)

    # Send data
    for index, loss in enumerate(train_loss_input):
        experiment.log_metric('Train Loss', loss, index)

    experiment.log_metric('Test Loss', test_loss_input[0], 0)

    time.sleep(2.5)

    # Schedule Aggregations
    request_schedule = create_schedule_aggregations_request_extensive()
    actual, _ = core_interface.create_response(request_schedule)

    time.sleep(1)

    # Get Aggregrations
    request_aggregations = create_get_aggregation_results_request_extensive()
    actual, _ = core_interface.create_response(request_aggregations)

    assert np.isclose(actual['get_average'], expected_mean, equal_nan=True).all() 
    assert np.isclose(actual['get_max'], expected_max, equal_nan=True).all() 
    assert np.isclose(actual['get_min'], expected_min, equal_nan=True).all()   
