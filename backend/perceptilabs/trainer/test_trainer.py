import os
import pytest
import pickle
import tempfile
from unittest.mock import MagicMock

import tensorflow as tf
import numpy as np
import pandas as pd

from perceptilabs.data.base import DataLoader
from perceptilabs.data.settings import FeatureSpec, Partitions, DatasetSettings
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.trainer import Trainer, TrainingModel
from perceptilabs.exporter.base import Exporter    


@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 45.0, -10.0], 'y1': [1.0, 2.0, 3.0, 4.0, -1.0]})
    df.to_csv(file_path, index=False)    
    yield file_path

    
@pytest.fixture()
def data_loader(csv_path):
    settings = DatasetSettings(
        file_path=csv_path,
        feature_specs={
            'x1': FeatureSpec(datatype='numerical', iotype='input'),
            'y1': FeatureSpec(datatype='numerical', iotype='target')            
        },
        partitions=Partitions(training_ratio=4/5, validation_ratio=1/5, test_ratio=0.0)
    )
    dl = DataLoader.from_settings(settings)
    yield dl

@pytest.fixture()
def training_settings():
    yield {
        'Epochs':10,
        'Batch_size':2,
        'Learning_rate':0.001,
        'Beta1':0.9,
        'Beta2':0.99,
        'Momentum':0.0,
        'Centered':False,
        'Loss':'Quadratic',
        'Optimizer':'SGD',
        'Shuffle': False,
        'AutoCheckpoint': False
    }

@pytest.fixture()
def training_settings_custom_loss(training_settings):
    training_settings['Loss'] = 'Dice'
    yield training_settings

    
@pytest.fixture()
def training_settings_shuffle_data(training_settings):
    training_settings['Shuffle'] = True
    yield training_settings
    
    
@pytest.fixture()
def graph_spec(csv_path):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1', 'file_path': csv_path}
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



@pytest.fixture()
def graph_spec_faulty(csv_path):
    gsb = GraphSpecBuilder()
    dirpath = tempfile.mkdtemp()
    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'datatype': 'numerical', 'feature_name': 'x1', 'file_path': csv_path}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 112}
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


@pytest.fixture
def training_model(graph_spec, script_factory):
    training_model = TrainingModel(script_factory, graph_spec)    
    yield training_model


@pytest.fixture
def training_model_faulty(graph_spec_faulty, script_factory):
    training_model = TrainingModel(script_factory, graph_spec_faulty)        
    yield training_model


@pytest.fixture
def exporter(graph_spec, training_model, data_loader):
    exporter = Exporter(graph_spec, training_model, data_loader)
    yield exporter


def test_progress_reaches_one(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    assert trainer.progress == 0.0 and trainer.num_epochs_completed == 0
    trainer.run()
    assert trainer.progress == 1.0 and trainer.num_epochs_completed == trainer.num_epochs


def test_trainer_has_all_statuses(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)

    seen_statuses = [trainer.status]

    result = None    
    sentinel = object()
    iterator = trainer.run_stepwise()
    
    while result != sentinel:
        result = next(iterator, sentinel)

        if trainer.status not in seen_statuses:
            seen_statuses.append(trainer.status)

    assert seen_statuses == ['Waiting', 'Training', 'Validation', 'Finished']
    
    
def test_num_completed_batches_are_ok(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    trainer.run()

    # Run some sanity checks
    assert trainer.num_batches_completed_all_epochs == trainer.num_batches_all_epochs
    assert trainer.num_batches_per_epoch*trainer.num_epochs == trainer.num_batches_all_epochs
    assert trainer.num_training_batches_completed_this_epoch > 0
    assert trainer.num_validation_batches_completed_this_epoch > 0
    assert trainer.num_training_batches_completed_this_epoch + trainer.num_validation_batches_completed_this_epoch == trainer.num_batches_completed_this_epoch
    assert trainer.num_batches_completed_this_epoch == trainer.num_batches_per_epoch


def test_num_completed_batches_are_ok_even_if_batch_size_is_larger_than_dataset(data_loader, training_model, training_settings):
    batch_size = 200
    training_settings['Batch_size'] = batch_size

    assert data_loader.get_dataset_size(partition='training') > 0 and data_loader.get_dataset_size(partition='training') < batch_size
    assert data_loader.get_dataset_size(partition='validation') > 0 and data_loader.get_dataset_size(partition='validation') < batch_size    
    
    trainer = Trainer(data_loader, training_model, training_settings)
    trainer.run()

    # Run some sanity checks
    assert trainer.num_batches_completed_all_epochs == trainer.num_batches_all_epochs
    assert trainer.num_batches_per_epoch*trainer.num_epochs == trainer.num_batches_all_epochs
    assert trainer.num_training_batches_completed_this_epoch > 0
    assert trainer.num_validation_batches_completed_this_epoch > 0
    assert trainer.num_training_batches_completed_this_epoch + trainer.num_validation_batches_completed_this_epoch == trainer.num_batches_completed_this_epoch
    assert trainer.num_batches_completed_this_epoch == trainer.num_batches_per_epoch
    

def test_layer_output_ok(csv_path, data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    df = pd.read_csv(csv_path)
    
    expected = df['x1'][0:2].to_numpy()
    actual = trainer.get_layer_output('0')
    
    assert np.all(actual == expected)
    

def test_layer_weights_is_array(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_weights('1')
    assert isinstance(value, np.ndarray)

    
def test_layer_bias_is_array(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_bias('1')
    assert isinstance(value, np.ndarray)
    

def test_layer_gradients_contain_exactly_one_float(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_weights('1')
    assert isinstance(value, np.ndarray)


def test_layer_bias_is_array(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_bias('1')
    assert isinstance(value, np.ndarray)
    

def test_layer_gradients_contain_exactly_one_float(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    minimum = trainer.get_layer_gradients('1', 'minimum')
    maximum = trainer.get_layer_gradients('1', 'maximum')
    average = trainer.get_layer_gradients('1', 'average')
    
    assert isinstance(minimum, list) and len(minimum) == 1 and isinstance(minimum[0], np.float32)
    assert isinstance(maximum, list) and len(maximum) == 1 and isinstance(maximum[0], np.float32)
    assert isinstance(average, list) and len(average) == 1 and isinstance(average[0], np.float32)
    assert minimum[0] <= maximum[0]

    
def test_layer_gradients_contain_exactly_one_float(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    minimum = trainer.get_layer_gradients('1', 'minimum')
    maximum = trainer.get_layer_gradients('1', 'maximum')
    average = trainer.get_layer_gradients('1', 'average')
    
    assert isinstance(minimum, list) and len(minimum) == 1 and isinstance(minimum[0], np.float32)
    assert isinstance(maximum, list) and len(maximum) == 1 and isinstance(maximum[0], np.float32)
    assert isinstance(average, list) and len(average) == 1 and isinstance(average[0], np.float32)
    assert minimum[0] <= maximum[0]

    
def test_computed_results_do_not_change(data_loader, training_model, training_settings):
    """ Once results have been computed, the Trainer shouldn't modify the structure.

    A simple way to test for that is to pickle the structure twice. 
    Once at the beginning of training and once after.

    Note: the results themselves should change
    """
    trainer = Trainer(data_loader, training_model, training_settings)

    step = trainer.run_stepwise()
    next(step)  # Take the first training steps

    initial_results = trainer.get_results()
    pickled_initial_results = pickle.dumps(initial_results)
        
    for _ in step:  # Complete training
        pass

    final_results = trainer.get_results()    
    pickled_final_results = pickle.dumps(final_results)
    repickled_initial_results = pickle.dumps(initial_results)
    
    assert pickled_initial_results != pickled_final_results  # The results should be different
    assert repickled_initial_results == pickled_initial_results  # But the initial results shouldn't change.
    

def test_trainer_target_stats_available(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    target_stats = trainer.get_target_stats()
    assert 'y1' in target_stats.sample_batch 

    
def test_trainer_prediction_stats_available(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    prediction_stats = trainer.get_prediction_stats()
    assert 'y1' in prediction_stats.sample_batch 

    
def test_trainer_input_stats_available(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps

    input_stats = trainer.get_input_stats()
    assert 'x1' in input_stats.sample_batch 


def test_trainer_can_pause_and_unpause(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    next(trainer.run_stepwise()) # Take the first training steps
    
    trainer.pause()
    assert trainer.status == 'Paused'

    trainer.unpause()
    assert trainer.status != 'Paused'


def test_trainer_can_stop(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)

    next(trainer.run_stepwise()) # Take the first training steps    
    trainer.stop()
    assert trainer.status == 'Finished'


def test_trainer_can_pause_stop(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)

    step = trainer.run_stepwise()
    next(step) # Take the first training steps    
    trainer.pause()
    next(step)
    trainer.stop()
    assert trainer.status == 'Finished'

    
def test_trainer_export_checkpoints_atleast_once(graph_spec, data_loader, training_model, training_settings, exporter, temp_path):
    trainer = Trainer(data_loader, training_model, training_settings, checkpoint_directory=temp_path, exporter=exporter)

    step = trainer.run_stepwise()
    next(step)  # Take the first training steps

    assert 'checkpoint' not in os.listdir(temp_path)

    for _ in step:  # Complete training
        pass

    assert len(os.listdir(temp_path)) > 0
    assert 'checkpoint' in os.listdir(temp_path)

    
def test_trainer_export_checkpoint_while_training(graph_spec, data_loader, training_model, training_settings, exporter, temp_path):
    trainer = Trainer(data_loader, training_model, training_settings, exporter=exporter, checkpoint_directory=temp_path)

    step = trainer.run_stepwise()
    next(step)  # Take the first training steps

    assert 'checkpoint' not in os.listdir(temp_path)

    trainer.export(temp_path, mode='Checkpoint')
    assert 'checkpoint' in os.listdir(temp_path)

    
def test_trainer_export_pb_while_training(graph_spec, data_loader, training_model, training_settings, exporter, temp_path):
    trainer = Trainer(data_loader, training_model, training_settings, exporter=exporter, checkpoint_directory=temp_path)

    step = trainer.run_stepwise()
    next(step)  # Take the first training steps

    assert 'saved_model.pb' not in os.listdir(temp_path)


def test_trainer_custom_loss(data_loader, training_model, training_settings_custom_loss):
    """ Tests if the trainer can finish a full training loop with a loss function not native to the Keras library, such as Dice. """
    
    trainer = Trainer(data_loader, training_model, training_settings_custom_loss)
    step = trainer.run_stepwise()
    next(step)  # Take the first training steps

    initial_results = trainer.get_results()
    assert initial_results is not None

    for _ in step:  # Complete training
        pass


def test_trainer_output_stats_available(graph_spec, data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    trainer.run()

    output_stats = trainer.get_output_stats()

    for layer_spec in graph_spec.target_layers:    
        assert layer_spec.id_ in output_stats

        
def test_shuffle_is_called_for_training_but_not_for_validation(csv_path, training_model, training_settings_shuffle_data):
    data_loader = MagicMock()
    data_loader.get_dataset_size.return_value = 10
    
    trainer = Trainer(data_loader, training_model, training_settings_shuffle_data)

    step = trainer.run_stepwise()

    for i, _ in enumerate(step):
        _, kwargs = data_loader.get_dataset.call_args_list[i*2]  # Even calls are with training
        assert kwargs['partition'] == 'training' and kwargs['shuffle']

        _, kwargs = data_loader.get_dataset.call_args_list[i*2 + 1]  # Odd calls are with validation
        assert kwargs['partition'] == 'validation' and ('shuffle' not in kwargs or not kwargs['shuffle'])        


def test_trainer_validate_raises_no_error(data_loader, training_model, training_settings):
    trainer = Trainer(data_loader, training_model, training_settings)
    trainer.validate()

    
def test_trainer_validate_raises_error_for_faulty_spec(data_loader, training_model_faulty, training_settings):
    trainer = Trainer(data_loader, training_model_faulty, training_settings)

    with pytest.raises(tf.errors.InvalidArgumentError):  # Expects an error since num neurons == 112, while output shape == 1
        trainer.validate()
        
    
def test_trainer_calls_export_checkpoint_once_per_epoch(graph_spec, data_loader, training_model, training_settings, temp_path):
    training_settings['AutoCheckpoint'] = True
    exporter = MagicMock()

    trainer = Trainer(data_loader, training_model, training_settings, exporter=exporter, checkpoint_directory=temp_path)
    step = trainer.run()

    assert exporter.export_checkpoint.call_count == training_settings['Epochs']


def test_trainer_load_from_initial_gives_equal_results(graph_spec, data_loader, training_model, training_settings):
    trainer1 = Trainer(data_loader, training_model, training_settings)

    step = trainer1.run_stepwise()    
    for _ in range(3):
        next(step)        

    saved_state = trainer1.save_state()
    trainer2 = Trainer(data_loader, training_model, training_settings, initial_state=saved_state)
    trainer2.ensure_data_initialized()  # Without this, some data dependent results may be wrong

    results1 = trainer1.get_results()
    results2 = trainer2.get_results()

    for key in results1:
        assert results1[key] == results2[key]
    


    

    
