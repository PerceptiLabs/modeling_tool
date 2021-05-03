import pytest
import os
import pytest
import pickle
import tempfile
from unittest.mock import MagicMock

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader, FeatureSpec    
from perceptilabs.script import ScriptFactory
from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter
from perceptilabs.trainer import Trainer

@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 45.0], 'y1': [1.0, 2.0, 3.0, 4.0]})
    df.to_csv(file_path, index=False)    
    yield file_path

    
@pytest.fixture()
def data_loader(csv_path):
    dl = DataLoader.from_features(
        {
            'x1': FeatureSpec('numerical', 'input', csv_path),
            'y1': FeatureSpec('numerical', 'output', csv_path)            
        }
    )
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
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y1', 'file_path': csv_path}
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


def test_create_exporter_from_graph(script_factory, graph_spec_few_epochs, temp_path):
    # Use data loader to feed data through the model
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model)
    assert exporter is not None


def test_save_training_model_weights(script_factory, graph_spec_few_epochs, temp_path):
    # Use data loader to feed data through the model
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    x = {'x1': np.array([1.0, 2.0, 3.0])}
    expected = training_model(x)

    exporter = Exporter(graph_spec_few_epochs, training_model)

    exporter.export_checkpoint(temp_path)
    assert len(os.listdir(temp_path)) > 0

    exporter = Exporter.from_disk(temp_path, graph_spec_few_epochs, script_factory)
    assert exporter is not None
    
    loaded_training_model = exporter.training_model

    actual = loaded_training_model(x)
    assert (actual[0]['y1'] == expected[0]['y1']).numpy().all()
    assert (actual[1]['1']['output'] == expected[1]['1']['output']).numpy().all()
