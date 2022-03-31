from ast import Call
import os
import pytest
import os
import time
from unittest.mock import MagicMock
from queue import Queue

import perceptilabs.utils
import tensorflow as tf

from perceptilabs.call_context import CallContext
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.training_interface import TrainingSessionInterface
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script.base import ScriptFactory
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.rygg import RyggWrapper
from perceptilabs.resources.tf_support_access import TensorflowSupportAccess



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
def test_results_are_stored(message_broker, data_loader, graph_spec, training_model, training_settings, results_interval, tmpdir, tensorflow_support_access):
    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    model_access = MagicMock()
    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    interface.run(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id='456',
        graph_settings=graph_spec.to_dict(),
        training_session_id='789',
        training_settings=training_settings,
        load_checkpoint=False,
        results_interval=results_interval
    )

    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][2]['progress'] == 1.0


@pytest.mark.parametrize("auto_checkpoint", [False, True])
def test_auto_checkpoint(monkeypatch, auto_checkpoint, message_broker, data_loader, graph_spec, training_model, training_settings, tmpdir, tensorflow_support_access):
    training_settings['AutoCheckpoint'] = auto_checkpoint

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    model_access = MagicMock()
    results_access = MagicMock()
    event_tracker = MagicMock()

    fn_export = MagicMock()
    from perceptilabs.sharing.exporter import Exporter
    monkeypatch.setattr(Exporter, "export_checkpoint", fn_export)

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    interface.run(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id='456',
        graph_settings=graph_spec.to_dict(),
        training_session_id='789',
        training_settings=training_settings,
        load_checkpoint=False,
    )

    expected_count = training_settings['Epochs'] if auto_checkpoint else 1

    assert epochs_access.save_state_dict.call_count == expected_count
    assert epochs_access.get_checkpoint_path.call_count == expected_count
    assert Exporter.export_checkpoint.call_count == expected_count


def test_stopping_mid_training(monkeypatch, queue, message_broker, data_loader, graph_spec, training_model, training_settings, tmpdir, tensorflow_support_access):
    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    model_access = MagicMock()
    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    model_id = '456'
    training_session_id = '789'

    step = interface.run_stepwise(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id=model_id,
        graph_settings=graph_spec.to_dict(),
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
    )

    for counter, _ in enumerate(step):
        progress = results_access.store.call_args[0][2]['progress']

        if progress > 0.5:
            expected_progress = progress
            queue.put({'event': 'training-stop', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})

    actual_progress = results_access.store.call_args[0][2]['progress']

    assert actual_progress == expected_progress < 1.0  # Assert progress doesnt change after stopping


def test_pausing_mid_training(queue, message_broker, data_loader, graph_spec, training_model, training_settings, tensorflow_support_access, tmpdir):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    model_id = '456'
    training_session_id = '789'

    step = interface.run_stepwise(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id=model_id,
        graph_settings=graph_spec.to_dict(),
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
        results_interval=None, # make sure we get results every iteration,
    )

    step_pause = 3
    step_unpause = 12
    steps_paused = step_unpause - step_pause

    status_list = []
    for counter, _ in enumerate(step):
        status = results_access.store.call_args[0][2]['trainingStatus']
        status_list.append(status)

        if counter == step_pause:
            queue.put({'event': 'training-pause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})
        elif counter == step_unpause:
            queue.put({'event': 'training-unpause', 'payload': {'model_id': model_id, 'training_session_id': training_session_id}})

    assert counter > step_unpause and (step_unpause > step_pause)  # Assert we paused/unpaused
    assert status_list.count('Paused') == steps_paused


def test_export_mid_training(monkeypatch, queue, message_broker, data_loader, graph_spec, training_model, training_settings, tmp_path, tensorflow_support_access, tmpdir):
    fn_export = MagicMock()

    from perceptilabs.sharing.exporter import Exporter
    monkeypatch.setattr(Exporter, "export", fn_export)

    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    model_id = '456'
    training_session_id = '789'
    user_email = 'a@b.test'
    user_id = 'a1234'

    step = interface.run_stepwise(
        CallContext({'user_email': user_email, 'user_id': user_id}),
        data_loader,
        model_id=model_id,
        graph_settings=graph_spec.to_dict(),
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
    )

    assert fn_export.call_count == 0

    step_export = 5
    for counter, _ in enumerate(step):
        progress = results_access.store.call_args[0][2]['progress']

        if counter == step_export:
            queue.put({
                'event': 'training-export',
                'payload': {
                    'model_id': model_id,
                    'training_session_id': training_session_id,
                    'export_directory': str(tmp_path),
                    'mode': 'Standard',
                    'user_email': user_email,
                    'user_id': user_id,
                }
            })

    assert counter > step_export  # Ensure we sent the request...
    assert fn_export.call_count == 1


@pytest.mark.parametrize("load_checkpoint", [False, True])
def test_load_checkpoint(monkeypatch, message_broker, data_loader, graph_spec, training_model, training_settings, load_checkpoint, tensorflow_support_access):
    from perceptilabs.trainer.model import TrainingModel

    fn_mock = MagicMock()
    fn_mock.return_value = training_model
    monkeypatch.setattr(TrainingModel, "from_graph_spec", fn_mock)

    rygg = MagicMock()
    rygg.get_model.return_value = {"location": "/tmp/my-checkpoint-dir"}

    epochs_access = EpochsAccess(rygg)
    results_access = MagicMock()
    event_tracker = MagicMock()
    model_access = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    interface.run(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id='456',
        graph_settings=graph_spec.to_dict(),
        training_session_id='789',
        training_settings=training_settings,
        load_checkpoint=load_checkpoint,
    )

    assert fn_mock.call_count == 1
    requested_checkpoint = fn_mock.call_args[1]['checkpoint_path']
    if load_checkpoint:
        assert requested_checkpoint is not None
    else:
        assert requested_checkpoint is None



@pytest.mark.parametrize("model_id,session_id,expect_finished", [
    ('correct', 'correct', False),  # Both correct - should stop
    ('incorrect', 'incorrect', True),  # Both wrong - wont stop
    ('incorrect', 'correct', True),  # Model id wrong - wont stop
    ('correct', 'incorrect', True),  # Session id wrong - wont stop
])

def test_ignores_stopping_for_different_interface(model_id, session_id, expect_finished, queue, message_broker, data_loader, graph_spec, training_model, training_settings, tmpdir, tensorflow_support_access):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    actual_model_id = 'correct'
    actual_training_session_id = 'correct'

    step = interface.run_stepwise(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id=actual_model_id,
        graph_settings=graph_spec.to_dict(),
        training_session_id=actual_training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
    )

    for counter, _ in enumerate(step):
        progress = results_access.store.call_args[0][2]['progress']

        if counter == 3:
            queue.put({'event': 'training-stop', 'payload': {'model_id': model_id, 'training_session_id': session_id}})

    assert counter > 3

    if expect_finished:
        assert progress == 1.0
    else:
        assert progress < 1.0


def test_errors_are_stored(monkeypatch, message_broker, data_loader, graph_spec, training_model, training_settings, tmpdir, tensorflow_support_access):
    error_message = "sdijasdisaj"

    def fake_call(*args, **kwargs):
        raise ValueError(error_message)

    monkeypatch.setattr(TrainingModel, '__call__', fake_call, raising=True)

    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access
    )

    interface.run(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id='456',
        graph_settings=graph_spec.to_dict(),
        training_session_id='789',
        training_settings=training_settings,
        load_checkpoint=False,
    )

    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][2]['error']['message']
    assert error_message in results_access.store.call_args[0][2]['error']['details']


def test_tf_memory_growth_enabled(message_broker, data_loader, graph_spec, training_model, training_settings):
    model_access = MagicMock()
    epochs_access = MagicMock()
    results_access = MagicMock()
    event_tracker = MagicMock()
    
    tf_support_access = MagicMock()
    tf_support_access.enable_tf_gpu_memory_growth.return_value = True

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tf_support_access
    )

    interface.run(
        call_context=CallContext({
            'project_id': 123,
            'user_token': 'fake token from auth header',
            'user_email': 'a@b.test',
        }),
        data_loader=data_loader,
        model_id='456',
        graph_settings=graph_spec.to_dict(),
        training_session_id='789',
        training_settings=training_settings,
        load_checkpoint=False,
        results_interval=None
    )

    assert tf_support_access.set_tf_dependencies.call_count > 0
    

@pytest.mark.parametrize("slowdown_rate", [0.0, 0.2])
def test_slowdown_is_detected(monkeypatch, slowdown_rate, queue, message_broker, data_loader, graph_spec, training_model, training_settings, tensorflow_support_access, tmpdir):
    max_slowdown_rate = 0.1

    fake_sentry_call = MagicMock()
    monkeypatch.setattr(perceptilabs.utils, 'send_message_to_sentry', fake_sentry_call, raising=True)

    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = os.path.join(tmpdir, 'some.ckpt')

    results_access = MagicMock()
    event_tracker = MagicMock()

    interface = TrainingSessionInterface(
        message_broker,
        event_tracker,
        model_access=model_access,
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access,
        max_slowdown_rate=max_slowdown_rate
    )

    model_id = '456'
    training_session_id = '789'

    step = interface.run_stepwise(
        CallContext({'user_email': 'a@b.test', 'user_id': 'a1234'}),
        data_loader,
        model_id=model_id,
        graph_settings=graph_spec.to_dict(),
        training_session_id=training_session_id,
        training_settings=training_settings,
        load_checkpoint=False,
        results_interval=None, # make sure we get results every iteration,
    )

    status_list = []
    for counter, _ in enumerate(step):
        time.sleep(slowdown_rate*counter)

    if slowdown_rate == 0:
        assert fake_sentry_call.call_count == 0
    else:
        assert fake_sentry_call.call_count == 1
        first_call_args = fake_sentry_call.call_args[0]
        assert "Training slowdown detected" in first_call_args
