import os
import pytest
import tempfile

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.data.base import DataLoader, FeatureSpec    
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter
from perceptilabs.testcore.base import TestCore
from perceptilabs.testcore.strategies.teststrategies import ConfusionMatrix, MetricsTable
from perceptilabs.issues import IssueHandler


@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 46, 52, 56, 3, 67, 32, 94], 'y1': [1, 0, 1, 0, 0, 0, 1, 1, 0, 0]})
    df.to_csv(file_path, index=False)    
    yield file_path
    
@pytest.fixture()
def data_loader(csv_path):
    dl = DataLoader.from_features(
        {
            'x1': FeatureSpec('numerical', 'input', csv_path),
            'y1': FeatureSpec('categorical', 'output', csv_path)            
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
def testcore(graph_spec_few_epochs, temp_path, script_factory):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model)
    exporter.export_checkpoint(temp_path)
    testcore = TestCore([1], IssueHandler())
    testcore.load_model(1, temp_path, graph_spec_few_epochs)
    testcore.load_data(graph_spec_few_epochs, csv_path, method='graph_spec')
    yield testcore

def test_confusion_matrix_computation(testcore, data_loader): 
    model_outputs = {
        'outputs': [{'y1': np.array([[9.5598471e-01, 3.6293268e-04]], dtype=np.float32)}], 
        'labels': [{'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)}]
    }
    compatible_output_layers = ['y1']
    confusion_matrix = ConfusionMatrix().run(model_outputs, compatible_output_layers)
    assert (confusion_matrix['y1'].numpy()==np.array([[0, 0],[1, 0]], dtype=np.int32)).all()                                                        

def test_metrics_table_computation(testcore, data_loader): 
    model_outputs = {
        'outputs': [{'y1': np.array([[0.9, 0.1]], dtype=np.float32)},
                    {'y1': np.array([[0.6, 0.4]], dtype=np.float32)}, 
                    {'y1': np.array([[0.3, 0.7]], dtype=np.float32)},
                    {'y1': np.array([[0.52, 0.48]], dtype=np.float32)}], 
        'labels': [{'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)},
                   {'y1': tf.constant(np.array([[1., 0.]]), dtype=tf.float32)}, 
                   {'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)}, 
                   {'y1': tf.constant(np.array([[1., 0.]]), dtype=tf.float32)}]
    }
    compatible_output_layers = ['y1']
    metrics_table = MetricsTable().run(model_outputs, compatible_output_layers)
    assert metrics_table == {'y1': {'categorical_accuracy': 0.75, 'top_k_categorical_accuracy': 1.0, 'precision': 0.75, 'recall': 0.75}}


