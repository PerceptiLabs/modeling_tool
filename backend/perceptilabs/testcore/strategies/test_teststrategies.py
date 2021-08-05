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
from perceptilabs.testcore.strategies.teststrategies import ConfusionMatrix, MetricsTable, OutputVisualization
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

def test_confusion_matrix_computation(data_loader):
    model_outputs = {
        'outputs': [{'y1': np.array([[9.5598471e-01, 3.6293268e-04]], dtype=np.float32)}],
        'targets': [{'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)}]
    }
    compatible_output_layers = ['y1']
    confusion_matrix = ConfusionMatrix().run(model_outputs, compatible_output_layers)
    assert (confusion_matrix['y1'].numpy()==np.array([[0, 0],[1, 0]], dtype=np.int32)).all()

def test_categorical_metrics_table_computation(data_loader):
    model_outputs = {
        'outputs': [{'y1': np.array([[0.9, 0.1]], dtype=np.float32)},
                    {'y1': np.array([[0.6, 0.4]], dtype=np.float32)},
                    {'y1': np.array([[0.3, 0.7]], dtype=np.float32)},
                    {'y1': np.array([[0.52, 0.48]], dtype=np.float32)}],
        'targets': [{'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)},
                   {'y1': tf.constant(np.array([[1., 0.]]), dtype=tf.float32)},
                   {'y1': tf.constant(np.array([[0., 1.]]), dtype=tf.float32)},
                   {'y1': tf.constant(np.array([[1., 0.]]), dtype=tf.float32)}]
    }
    compatible_output_layers = {'y1':'categorical'}
    metrics_table = MetricsTable().run(model_outputs, compatible_output_layers)
    assert metrics_table == {'y1': {'categorical_accuracy': 0.75, 'top_k_categorical_accuracy': 1.0, 'precision': 0.75, 'recall': 0.75}}

def test_image_metrics_table_computation():
    m1 = np.array([[0.6,0.7],[0.4, 0.9]]).astype(np.float32)
    m2 = np.array([[0.4, 0.1],[0.2, 0.6]]).astype(np.float32)

    p1 = np.array([[1,0],[0,1]])
    p2 = np.array([[0,0],[1,1]])
    model_outputs = {
        'outputs': [{'y1': m1},
                    {'y1': m2}],
        'targets': [{'y1': tf.constant(p1, dtype=tf.float32)},
                   {'y1': tf.constant(p2, dtype=tf.float32)}]
    }
    compatible_output_layers = {'y1':'image'}
    metrics_table = MetricsTable().run(model_outputs, compatible_output_layers)
    assert metrics_table == {'y1':{'IoU': 0.6, 'dice_coefficient': 0.72, 'keras_dice_coefficient': 0.58}}

def test_outputs_visualization_computation():
    model_outputs = {
        'outputs': 5*[{'y1': np.random.random((512,512,1)).astype(np.float32)},
                    {'y1': np.random.random((512,512,1)).astype(np.float32)},
                    {'y1': np.random.random((512,512,1)).astype(np.float32)},
                    {'y1': np.random.random((512,512,1)).astype(np.float32)}],
        'targets': 5*[{'y1': tf.constant(np.random.randint(2, size=(512,512,1)), dtype=tf.float32)},
                   {'y1': tf.constant(np.random.randint(2, size=(512,512,1)), dtype=tf.float32)},
                   {'y1': tf.constant(np.random.randint(2, size=(512,512,1)), dtype=tf.float32)},
                   {'y1': tf.constant(np.random.randint(2, size=(512,512,1)), dtype=tf.float32)}]
    }
    model_inputs = 5*[{'x1': np.random.random((512,512,3)).astype(np.float32)},
                    {'x1': np.random.random((512,512,3)).astype(np.float32)},
                    {'x1': np.random.random((512,512,3)).astype(np.float32)},
                    {'x1': np.random.random((512,512,3)).astype(np.float32)}]

    compatible_output_layers = {'y1':'image'}

    results = OutputVisualization().run(model_inputs, model_outputs, compatible_output_layers)
    assert set(results['y1'].keys()) == {'inputs', 'targets', 'predictions', 'losses'}
    assert len(results['y1']['inputs']) == len(results['y1']['targets']) == len(results['y1']['targets']) == 10
    assert type(results['y1']['inputs'][0]) is np.ndarray
