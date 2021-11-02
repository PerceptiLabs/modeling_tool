import os
import pytest
import tempfile

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings, FeatureSpec
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter
from perceptilabs.testcore.base import TestCore, ProcessResults
from perceptilabs.resources.files import FileAccess


@pytest.fixture()
def data_loader():
    builder = DatasetBuilder.from_features({
        'x1': {'datatype': 'numerical', 'iotype': 'input'},
        'y1': {'datatype': 'categorical', 'iotype': 'target'}
    })

    with builder:
        builder.add_row({'x1': 123.0, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 24.0, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 13.0, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 46, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 52, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 56, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 3, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 67, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 32, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 94, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 16, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 55, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 61, 'y1': 1}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 33, 'y1': 0}, dtypes={'y1': np.int32})
        builder.add_row({'x1': 92, 'y1': 0}, dtypes={'y1': np.int32})
        
        dl = builder.get_data_loader()
        yield dl


@pytest.fixture()
def graph_spec_few_epochs():
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1'}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 2}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'categorical', 'feature_name': 'y1'}
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


@pytest.fixture()
def training_session_id(temp_path):
    import base64    
    return base64.urlsafe_b64encode(temp_path.encode()).decode()


@pytest.fixture()
def testcore(graph_spec_few_epochs, temp_path, script_factory, data_loader, training_session_id):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)
    checkpoint_path = os.path.join(temp_path, 'checkpoint-0000.ckpt')
    exporter.export_checkpoint(checkpoint_path)
    models_info = {
        1: {
            'graph_spec': graph_spec_few_epochs,
            'training_session_id': training_session_id,
            'data_loader': data_loader,
            'model_name': 'unit test'
        },
        2: {
            'graph_spec': graph_spec_few_epochs,
            'training_session_id': training_session_id,
            'data_loader': data_loader,
            'model_name': 'unit test'
        },
        3: {
            'graph_spec': graph_spec_few_epochs,
            'training_session_id': training_session_id,
            'data_loader': data_loader,
            'model_name': 'unit test'
        },
    }
    tests = []
    testcore = TestCore(training_session_id, [1], models_info, tests)
    testcore.load_models_and_data()
    yield testcore

    
def test_testcore_is_loading_data(testcore, data_loader):
    assert type(data_loader).__name__ == 'DataLoader'
    dataset_generator = data_loader.get_dataset(partition='test').batch(1)
    for input_1, _ in dataset_generator:
        data1 = input_1
    for input_2, _ in testcore._get_data_generator(1):
        data2 = input_2
    assert data1 == data2

    
def test_model_is_loaded_from_checkpoint(testcore):
    assert testcore._models[1]._model is not None

    
def test_model_outputs_structure_is_accurate(testcore):
    data_iterator = testcore._get_data_generator(1)
    model_inputs, model_outputs = testcore.models[1].run_inference(data_iterator)
    assert list(model_outputs.keys()) == ['outputs', 'targets']
    assert list(model_outputs['outputs'][0].keys()) == ['y1']
    assert list(model_outputs['targets'][0].keys()) == ['y1']

    
def test_model_has_compatible_output_layers_for_confusionmatrix(testcore):
    layers = testcore.get_compatible_output_layers('confusion_matrix', 1)
    assert layers == {'y1':'categorical'}


def test_status_messages(testcore, data_loader):
    num_models = len(testcore.models)
    num_samples = data_loader.get_dataset_size(partition='test')
    
    status_messages = []
    
    for step in iter(testcore.run_stepwise()):
        status = testcore.get_testcore_status()
        status_messages.append(status)

    assert len(status_messages) == num_models*num_samples + 1 # one message per sample and +1 for the initial "loading models" message...





