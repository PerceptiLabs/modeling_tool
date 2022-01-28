import pytest
from unittest.mock import MagicMock
from queue import Queue

import tensorflow as tf

from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.testing_interface import TestingSessionInterface
from perceptilabs.script.base import ScriptFactory


def make_session_id(string):
    import base64    
    return base64.urlsafe_b64encode(string.encode()).decode()    


@pytest.fixture
def data_loader():    
    builder = DatasetBuilder.from_features({
        'x': {'datatype': 'numerical', 'iotype': 'input'},
        'y': {'datatype': 'categorical', 'iotype': 'target'},
    })
    num_samples = 4
    with builder:
        for _ in range(num_samples):
            builder.add_row({'x': 1.0, 'y': 'a'})
            
        yield builder.get_data_loader()


@pytest.fixture()
def graph_spec():
    gsb = GraphSpecBuilder()

    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x'}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y'}
    )

    # Connect the layers
    gsb.add_connection(
        source_id=id1, source_var='output',
        dest_id=id2, dest_var='input'
    )
    gsb.add_connection(
        source_id=id2, source_var='output',
        dest_id=id3, dest_var='input'
    )

    graph_spec = gsb.build()
    return graph_spec


@pytest.fixture(scope='function')
def queue():
    return Queue()


@pytest.fixture(scope='function')    
def message_broker(queue):
    broker = MagicMock()
    broker.subscription.return_value.__enter__.return_value = queue
    yield broker


@pytest.mark.parametrize("results_interval", [None, 0.0001])
def test_results_are_stored(message_broker, data_loader, graph_spec, results_interval, temp_path):
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    results_access = MagicMock()
    event_tracker = MagicMock()
    
    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    tests = ['confusion_matrix']    
    
    interface.run(
        testing_session_id='123',
        models={
            '111': {
                'graph_spec': graph_spec,
                'data_loader': data_loader,
                'model_name': 'model111',
                'training_session_id': '134'
            }
        },
        tests=tests,
        user_email='a@b.com',
        results_interval=results_interval
    )

    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][1]['status']['status'] == 'Completed'
    for test in tests:
        assert results_access.store.call_args[0][1]['results'][test] != {}


def test_stopping_mid_training(monkeypatch, queue, message_broker, data_loader, graph_spec, temp_path):
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None
    
    results_access = MagicMock()
    event_tracker = MagicMock()        
    
    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    tests = ['confusion_matrix']    

    testing_session_id = '123', 
    
    step = interface.run_stepwise(
        testing_session_id=testing_session_id,
        models={
            '111': {
                'graph_spec': graph_spec,
                'data_loader': data_loader,
                'model_name': 'model111',
                'training_session_id': make_session_id(temp_path)
            }
        },
        tests=tests,
        user_email='a@b.com',
    )
    
    for counter, _ in enumerate(step):
        if counter == 0:  # Stop after 3 steps
            expected_results = results_access.store.call_args[0][1]['results']
            queue.put(
                {'event': 'testing-stop', 'payload': {'testing_session_id': testing_session_id}})

    actual_results = results_access.store.call_args[0][1]['results']            

    assert counter > 0  # Assert we actuall went further than just the first iteration
    assert actual_results == expected_results # Assert results doesnt change after stopping
    assert results_access.store.call_args[0][1]['status']['status'] == 'Stopped'

