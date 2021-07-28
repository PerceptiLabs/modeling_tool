import os
import pytest
import tempfile

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import DatasetSettings, FeatureSpec
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter
from perceptilabs.testcore.base import TestCore, ProcessResults
from perceptilabs.issues import IssueHandler


@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 46, 52, 56, 3, 67, 32, 94], 'y1': [1, 0, 1, 0, 0, 0, 1, 1, 0, 0]})
    df.to_csv(file_path, index=False)
    yield file_path


@pytest.fixture()
def data_loader(csv_path):
    settings = DatasetSettings(
        file_path=csv_path,
        feature_specs={
            'x1': FeatureSpec(datatype='numerical', iotype='input'),
            'y1': FeatureSpec(datatype='categorical', iotype='target')
        },
    )
    dl = DataLoader.from_settings(settings)
    yield dl


@pytest.fixture()
def graph_spec_few_epochs(csv_path):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1', 'file_path': csv_path, 'checkpoint_path':dirpath}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 2}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'categorical', 'feature_name': 'y1', 'file_path': csv_path}
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
def testcore(graph_spec_few_epochs, temp_path, script_factory, data_loader):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)
    exporter.export_checkpoint(temp_path)
    models_info = {
        1: {
            'graph_spec': graph_spec_few_epochs,
            'checkpoint_directory': temp_path,
            'data_path': csv_path,
            'data_loader': data_loader,
            'model_name': 'unit test'
        }
    }
    tests = []
    testcore = TestCore([1], models_info, tests, IssueHandler())
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
    model_outputs = testcore._models[1].run_inference(data_iterator)
    assert list(model_outputs.keys()) == ['outputs', 'labels']
    assert list(model_outputs['outputs'][0].keys()) == ['y1']
    assert list(model_outputs['labels'][0].keys()) == ['y1']

def test_model_has_compatible_output_layers_for_confusionmatrix(testcore):
    layers = testcore.get_compatible_output_layers('confusion_matrix', 1)
    assert layers == {'y1':'categorical'}










