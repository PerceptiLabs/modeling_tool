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
from perceptilabs.script import ScriptFactory
from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, DatasetSettings
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.exporter.base import Exporter


@pytest.fixture()
def data_loader():
    x1 = [123.0, 24.0, 13.0, 45.0, 20.0, 200.0, 421.0, 300.0, 254.0, 217.0, 363.0, 500.0]
    y1 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    df = pd.DataFrame({'x1': x1, 'y1': y1})

    feature_specs = {
        'x1': FeatureSpec(iotype='input', datatype='numerical'),
        'y1': FeatureSpec(iotype='target', datatype='numerical')
    }

    dataset_settings = DatasetSettings(feature_specs=feature_specs)
    dl = DataLoader(df, dataset_settings)
    yield dl


@pytest.fixture()
def graph_spec_few_epochs():
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1'}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'datatype': 'numerical', 'feature_name': 'y1'}
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


def equal_layer_outputs(dict1, dict2):
    """ Checks if two layers have equal output """
    if dict1.keys() != dict2.keys():
        return False

    for var_name in dict1.keys():
        values1 = dict1[var_name].numpy()
        values2 = dict2[var_name].numpy()

        if not np.all(values1 == values2):
            return False

    return True


def equal_training_model_outputs(all1, all2):
    """ Checks if two training models have equal output """
    output1, hidden1 = all1
    output2, hidden2 = all2

    if not equal_layer_outputs(output1, output2):
        return False

    if hidden1.keys() != hidden2.keys():
        return False

    for layer_id in hidden1.keys():
        if not equal_layer_outputs(hidden1[layer_id], hidden2[layer_id]):
            return False

    return True


def test_create_exporter_from_graph(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    # Use data loader to feed data through the model
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)
    assert exporter is not None


def test_export_training_model(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    exporter.export(target_dir, mode='Standard')

    assert os.path.isfile(os.path.join(target_dir, 'saved_model.pb'))
    assert os.path.isdir(os.path.join(target_dir, 'variables'))
    assert os.path.isdir(os.path.join(target_dir, 'assets'))


def test_export_compressed_model(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    exporter.export(target_dir, mode='Compressed')

    assert os.path.isfile(os.path.join(target_dir, 'model.tflite'))


def test_export_quantized_model(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'inference_model')
    assert not os.path.isdir(target_dir)

    output = exporter.export(target_dir, mode='Quantized')
    assert (os.path.isfile(os.path.join(target_dir, 'quantized_model.tflite')) or output)

def test_export_checkpoint_creates_files(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)
    target_dir = os.path.join(temp_path, 'checkpoint_dir')
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    exporter.export_checkpoint(target_dir)
    ckpt = tf.train.latest_checkpoint(target_dir)
    assert ckpt is not None
    training_model.load_weights(ckpt).assert_consumed()


def test_export_checkpoint_creates_multiple_files(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)

    target_dir = os.path.join(temp_path, 'checkpoint_dir')
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    exporter.export_checkpoint(target_dir, epoch=0)
    first_ckpt = tf.train.latest_checkpoint(target_dir)
    assert first_ckpt is not None
    training_model.load_weights(first_ckpt).assert_consumed()

    exporter.export_checkpoint(target_dir, epoch=1)
    second_ckpt = tf.train.latest_checkpoint(target_dir)
    assert second_ckpt is not None
    assert second_ckpt != first_ckpt

    training_model.load_weights(second_ckpt).assert_consumed() # Make sure weights can be loaded
    training_model.load_weights(first_ckpt).assert_consumed() # Make sure 1st ckpt is still valid


def test_loading_different_checkpoints_consistent_results(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)

    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)
    target_dir = os.path.join(temp_path, 'checkpoint_dir')

    inputs, targets = next(iter(data_loader.get_dataset().batch(2)))

    # Infer and export for epoch 0
    expected_output_epoch_0 = training_model(inputs)
    exporter.export_checkpoint(target_dir, epoch=0)
    ckpt_epoch_0 = tf.train.latest_checkpoint(target_dir)

    # Update the weights with random values to simulate a new epoch
    epoch_0_weights = training_model.get_weights()
    epoch_1_weights = [np.random.random() * w for w in epoch_0_weights]
    training_model.set_weights(epoch_1_weights)

    # Infer and export for epoch 1
    expected_output_epoch_1 = training_model(inputs)
    exporter.export_checkpoint(target_dir, epoch=1)
    ckpt_epoch_1 = tf.train.latest_checkpoint(target_dir)

    # Check that two different checkpoints exist
    assert ckpt_epoch_0 != ckpt_epoch_1

    # Load weights from epoch 0 and check consistent output
    training_model.load_weights(ckpt_epoch_0)
    actual_output_epoch_0 = training_model(inputs)
    assert equal_training_model_outputs(
        actual_output_epoch_0, expected_output_epoch_0)

    # Load weights from epoch 1 and check consistent output
    training_model.load_weights(ckpt_epoch_1)
    actual_output_epoch_1 = training_model(inputs)
    assert equal_training_model_outputs(
        actual_output_epoch_1, expected_output_epoch_1)

    # Check that the models produced different outputs for each epoch
    assert not equal_training_model_outputs(actual_output_epoch_0, actual_output_epoch_1)
    assert not equal_training_model_outputs(expected_output_epoch_0, expected_output_epoch_1)


def test_restore_model_from_disk(script_factory, graph_spec_few_epochs, data_loader, temp_path):
    # Use data loader to feed data through the model
    training_model = TrainingModel(script_factory, graph_spec_few_epochs)
    x = {'x1': np.array([1.0, 2.0, 3.0])}
    expected = training_model(x)

    exporter = Exporter(graph_spec_few_epochs, training_model, data_loader)

    exporter.export_checkpoint(temp_path)
    assert len(os.listdir(temp_path)) > 0

    # Create an equivalent model using the checkpoint
    exporter = Exporter.from_disk(
        temp_path, graph_spec_few_epochs, script_factory, data_loader)
    assert exporter is not None

    loaded_training_model = exporter.training_model
    assert loaded_training_model != training_model

    actual = loaded_training_model(x)
    assert (actual[0]['y1'] == expected[0]['y1']).numpy().all()
    assert (actual[1]['1']['output'] == expected[1]
            ['1']['output']).numpy().all()
