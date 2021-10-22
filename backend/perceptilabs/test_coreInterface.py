import pytest
from unittest.mock import MagicMock
from queue import Queue

import tensorflow as tf

from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.coreInterface import TrainingSessionInterface
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script.base import ScriptFactory


def make_session_id(string):
    import base64    
    return base64.urlsafe_b64encode(string.encode()).decode()    


@pytest.fixture
def data_loader():    
    builder = DatasetBuilder.from_features({
        'x': {'datatype': 'numerical', 'iotype': 'input'},
        'y': {'datatype': 'numerical', 'iotype': 'target'},
    })
    num_samples = 4
    with builder:
        for _ in range(num_samples):
            builder.add_row({'x': 1.0, 'y': 2.0})
            
        yield builder.get_data_loader()


@pytest.fixture()
def graph_spec(csv_path):
    gsb = GraphSpecBuilder()
    # Create the layers
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


@pytest.fixture
def training_model(graph_spec):
    model = TrainingModel(ScriptFactory(), graph_spec)
    return model


@pytest.fixture()
def training_settings():
    yield {
        'Epochs': 5,
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


@pytest.fixture(scope='function')
def queue():
    return Queue()


@pytest.fixture(scope='function')    
def message_broker(queue):
    broker = MagicMock()
    broker.subscription.return_value.__enter__.return_value = queue
    yield broker


@pytest.mark.parametrize("results_interval", [None, 0.0001])
def test_results_are_stored(message_broker, data_loader, graph_spec, training_model, training_settings, results_interval):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )
    
    interface.run(
        data_loader,
        model_id='456',
        training_session_id=make_session_id('789'),
        training_settings=training_settings,
        load_checkpoint=False,
        user_email='a@b.com',
        results_interval=results_interval
    )
    
    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][1]['progress'] == 1.0


def test_stopping_mid_training(monkeypatch, queue, message_broker, data_loader, graph_spec, training_model, training_settings):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    model_id = '456'
    training_session_id = make_session_id('789')
    
    step = interface.run_stepwise(
        data_loader,
        model_id=model_id,
        training_session_id=training_session_id,  
        training_settings=training_settings,
        load_checkpoint=False,
        user_email='a@b.com'
    )

    for counter, _ in enumerate(step):
        expected_progress = results_access.store.call_args[0][1]['progress']

        if expected_progress > 0.5:
            queue.put({'event': 'training-stop', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})
        
    actual_progress = results_access.store.call_args[0][1]['progress']    
    
    assert actual_progress == expected_progress < 1.0  # Assert progress doesnt change after stopping
    

def test_pausing_mid_training(queue, message_broker, data_loader, graph_spec, training_model, training_settings):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    model_id = '456'
    training_session_id = make_session_id('789')
    
    step = interface.run_stepwise(
        data_loader,
        model_id=model_id,
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
        user_email='a@b.com',
        results_interval=None, # make sure we get results every iteration,
    )

    step_pause = 3
    step_unpause = 12
    steps_paused = step_unpause - step_pause
    
    status_list = []
    for counter, _ in enumerate(step):
        status = results_access.store.call_args[0][1]['trainingStatus']
        status_list.append(status)
        
        if counter == step_pause:
            queue.put({'event': 'training-pause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})            
        elif counter == step_unpause:
            queue.put({'event': 'training-unpause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})                        
    
    assert counter > step_unpause and (step_unpause > step_pause)  # Assert we paused/unpaused
    assert status_list.count('Paused') == steps_paused


def test_export_mid_training(monkeypatch, queue, message_broker, data_loader, graph_spec, training_model, training_settings, tmp_path):
    fn_export = MagicMock()

    from perceptilabs.exporter.base import Exporter
    monkeypatch.setattr(Exporter, "export", fn_export)  
    
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    model_id = '456'
    training_session_id = make_session_id('789')
    
    step = interface.run_stepwise(
        data_loader,
        model_id=model_id,
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
        user_email='a@b.com'
    )

    assert fn_export.call_count == 0    

    step_export = 5
    for counter, _ in enumerate(step):
        progress = results_access.store.call_args[0][1]['progress']

        if counter == step_export:
            queue.put({
                'event': 'training-export',
                'payload': {
                    'model_id': model_id,
                    'training_session_id': training_session_id,
                    'export_directory': str(tmp_path),
                    'mode': 'Standard'
                }
            })

    assert counter > step_export  # Ensure we sent the request...
    assert fn_export.call_count == 1

    

@pytest.mark.parametrize("load_checkpoint", [False, True])
def test_load_checkpoint(message_broker, data_loader, graph_spec, training_model, training_settings, load_checkpoint):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )
    
    interface.run(
        data_loader,
        model_id='456',
        training_session_id=make_session_id('789'),
        training_settings=training_settings,
        load_checkpoint=load_checkpoint,
        user_email='a@b.com'
    )

    assert model_access.get_training_model.call_count == 1

    requested_checkpoint = model_access.get_training_model.call_args.kwargs['checkpoint_path']
    if load_checkpoint:
        assert requested_checkpoint is not None
    else:
        assert requested_checkpoint is None

        

@pytest.mark.parametrize("model_id,session_id,expect_finished", [
    ('correct', make_session_id('correct'), False),  # Both correct - should stop
    ('incorrect', make_session_id('incorrect'), True),  # Both wrong - wont stop
    ('incorrect', make_session_id('correct'), True),  # Model id wrong - wont stop
    ('correct', make_session_id('incorrect'), True),  # Session id wrong - wont stop         
])
                         
def test_ignores_stopping_for_different_interface(model_id, session_id, expect_finished, queue, message_broker, data_loader, graph_spec, training_model, training_settings):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    results_access = MagicMock()
    
    interface = TrainingSessionInterface(
        message_broker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access
    )

    actual_model_id = 'correct'
    actual_training_session_id = make_session_id('correct')
    
    step = interface.run_stepwise(
        data_loader,
        model_id=actual_model_id,
        training_session_id=actual_training_session_id,  
        training_settings=training_settings,
        load_checkpoint=False,
        user_email='a@b.com'
    )

    for counter, _ in enumerate(step):
        progress = results_access.store.call_args[0][1]['progress']

        if counter == 3:
            queue.put({'event': 'training-stop', 'payload': {'model_id': model_id, 'training_session_id': session_id}})

    assert counter > 3

    if expect_finished:
        assert progress == 1.0
    else:
        assert progress < 1.0

        
