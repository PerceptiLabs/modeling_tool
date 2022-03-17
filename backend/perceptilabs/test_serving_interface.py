import pytest
import json
import time
import os
import io
import requests
import zipfile
from retrying import retry
from unittest.mock import MagicMock
from queue import Queue

from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.serving_interface import ServingSessionInterface
from perceptilabs.script.base import ScriptFactory
from perceptilabs.resources.serving_results import ServingResultsAccess
from perceptilabs.resources.model_archives import ModelArchivesAccess
import perceptilabs.sharing.fastapi_utils as fastapi_utils


@pytest.fixture
def rygg_mock(temp_path):
    class RyggMock:
        def get_model(self, call_context, model_id):
            return {'location': temp_path}

    return RyggMock()


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

    
@pytest.mark.parametrize("export_type", ["Standard", "FastAPI", "PlPackage"])    
def test_zipfile_is_written_to_writable_path(export_type, message_broker, data_loader, graph_spec, temp_path, tensorflow_support_access):
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    model_archives_access = MagicMock()    

    results_access = MagicMock()
    results_access.get_serving_directory.return_value = temp_path

    event_tracker = MagicMock()

    serving_settings = {
        'mode': 'zip',
        'exportSettings': {
            'Type': export_type,
        },
        'ExcludePreProcessing': False,
        'ExcludePostProcessing': False,        
    }

    interface = ServingSessionInterface(
        serving_settings,
        message_broker,
        event_tracker,
        model_access=model_access,
        model_archives_access=model_archives_access,        
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access,
        ttl=10
    )

    step = interface.run_stepwise(
        {}, data_loader,
        '123', '456', '789', 'my_model')
    next(step)

    archive_dest = model_archives_access.write.call_args.args[0]
    assert archive_dest == os.path.join(temp_path, 'model.zip')
    
    extra_files = {
        os.path.basename(file_path)
        for file_path in model_archives_access.write.call_args.kwargs['extra_files']
    }

    inference_model_files = {
        'saved_model.pb',
        'keras_metadata.pb',
        'variables',
        'assets'
    }
    if export_type == 'Standard':
        expected_files = inference_model_files
    elif export_type == 'FastAPI':
        fastapi_files = {
            fastapi_utils.SCRIPT_FILE,
            fastapi_utils.REQUIREMENTS_FILE,
            fastapi_utils.EXAMPLE_JSON_FILE,
            fastapi_utils.EXAMPLE_SCRIPT_FILE,
            fastapi_utils.EXAMPLE_CSV_FILE,
            fastapi_utils.EXAMPLE_REQUIREMENTS_FILE            
        }
        expected_files = set.union(
            inference_model_files, fastapi_files)
    elif export_type == 'PlPackage':
        expected_files = set()  

    assert extra_files == expected_files


def test_zipfile_has_model_json(rygg_mock, message_broker, data_loader, graph_spec, temp_path, tensorflow_support_access):
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    model_archives_access = ModelArchivesAccess()
    results_access = ServingResultsAccess(rygg=rygg_mock)

    event_tracker = MagicMock()

    graph_settings = {'abc': '123'}
    training_settings = {'def': '456'}
    dataset_settings = {'xyz': '789'}            
    frontend_settings = {'wasd': '1234'}
    
    serving_settings = {
        'mode': 'zip',
        'exportSettings': {
            'Type': 'PlPackage',
        },
        'ExcludePreProcessing': False,
        'ExcludePostProcessing': False,
        'datasetSettings': dataset_settings,
        'graphSettings': graph_settings,
        'trainingSettings': training_settings,
        'frontendSettings': frontend_settings,
    }

    interface = ServingSessionInterface(
        serving_settings,
        message_broker,
        event_tracker,
        model_access=model_access,
        model_archives_access=model_archives_access,        
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access,
        ttl=10
    )
    serving_session_id = results_access.new_id({}, '123')
    
    step = interface.run_stepwise(
        {}, data_loader,
        '123', '456', serving_session_id, 'my_model')
    next(step)

    archive_path = results_access.get_served_zip(serving_session_id)
    
    with zipfile.ZipFile(archive_path, 'r') as archive:
        model_json = archive.read('model.json').decode('utf-8')
        content = json.loads(model_json)

    assert content['datasetSettings'] == dataset_settings
    assert content['graphSettings'] == graph_settings
    assert content['trainingSettings'] == training_settings
    assert content['frontendSettings'] == frontend_settings


def test_cleanup_after_ttl(message_broker, data_loader, graph_spec, temp_path, tensorflow_support_access):
    num_seconds_to_live = 5 # seconds
    
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    model_archives_access = MagicMock()    

    results_access = MagicMock()
    results_access.get_serving_directory.return_value = temp_path

    event_tracker = MagicMock()

    serving_settings = {
        'mode': 'zip',
        'exportSettings': {
            'Type': 'Standard',
        },
        'ExcludePreProcessing': False,
        'ExcludePostProcessing': False,
        'ttl': num_seconds_to_live
    }

    on_cleanup = MagicMock()

    interface = ServingSessionInterface(
        serving_settings,
        message_broker,
        event_tracker,
        model_access=model_access,
        model_archives_access=model_archives_access,        
        epochs_access=epochs_access,
        results_access=results_access,
        tensorflow_support_access=tensorflow_support_access,
        ttl=num_seconds_to_live,
    )

    serving_session_id = '789'
    results_interval = 1.0

    step = interface.run_stepwise(
        {},
        data_loader,
        '123', '456', serving_session_id, 'my_model',
        results_interval=results_interval,
    )
    next(step)  # Take an initial step to start the serving up

    t_start = time.perf_counter()
    t_elapsed = lambda: time.perf_counter() - t_start

    for _ in step:
        if t_elapsed() < num_seconds_to_live:
            assert results_access.remove.call_count == 0
        else:
            assert results_access.remove.call_count == 1
            assert results_access.remove.call_args.args == (serving_session_id,)

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_ttl():
        assert t_elapsed() >= num_seconds_to_live
        assert results_access.remove.call_count == 1
        assert results_access.remove.call_args.args == (serving_session_id,)
        
    wait_for_ttl()
            
def zip_file_names(path):
    with zipfile.ZipFile(path, 'r') as archive:
        return set(archive.namelist())
    

def test_serve_two_different_models(rygg_mock, message_broker, data_loader, graph_spec, temp_path):
    results_access = ServingResultsAccess(rygg=rygg_mock)
    
    tf_support_access = MagicMock()
    
    model_access = MagicMock()
    model_access.get_graph_spec.return_value = graph_spec

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    model_archives_access = ModelArchivesAccess()
    event_tracker = MagicMock()


    def serve_model(serving_session_id, export_settings):
        settings = {
            'mode': 'zip',
            'exportSettings': export_settings,
            'ExcludePreProcessing': False,
            'ExcludePostProcessing': False,        
        }
    
        interface = ServingSessionInterface(
            settings,
            message_broker,
            event_tracker,
            model_access=model_access,
            model_archives_access=model_archives_access,        
            epochs_access=epochs_access,
            results_access=results_access,
            tensorflow_support_access=tf_support_access,
            ttl=3600
        )

        return interface.run_stepwise(
            {},
            data_loader,
            '123',
            '456',
            serving_session_id,
            'my_model',
        )

    serving_session_a = results_access.new_id({}, '123')
    step_a = serve_model(
        serving_session_id=serving_session_a,
        export_settings={'Type': 'Standard'}
    )
    next(step_a)

    serving_session_b = results_access.new_id({}, '123')    
    step_b = serve_model(
        serving_session_id=serving_session_b,
        export_settings={'Type': 'Compressed'}
    )
    next(step_b)    
    
    path_a = results_access.get_served_zip(serving_session_a)
    path_b = results_access.get_served_zip(serving_session_b)

    assert os.path.isfile(path_a)
    assert path_a.endswith('model.zip')

    assert os.path.isfile(path_b)
    assert path_b.endswith('model.zip')    

    assert path_a != path_b
    assert zip_file_names(path_a) != zip_file_names(path_b)

    
    
