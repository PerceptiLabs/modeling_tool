import os
import pytest
import pickle
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

from perceptilabs.data.base import DataLoader, FeatureSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.trainer import Trainer


@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 45.0, -10.0], 'y1': [1.0, 2.0, 3.0, 4.0, -1.0]})
    df.to_csv(file_path, index=False)    
    yield file_path

    
@pytest.fixture()
def data_loader(csv_path):
    dl = DataLoader.from_features(
        {
            'x1': FeatureSpec('numerical', 'input', csv_path),
            'y1': FeatureSpec('numerical', 'output', csv_path)            
        },
        partitions={'training': 4/5, 'validation': 1/5, 'test': 0.0}
    )
    yield dl

    
@pytest.fixture()
def graph_spec_few_epochs(csv_path):
    gsb = GraphSpecBuilder()

    # Create the layers
    id1 = gsb.add_layer(
        'IoInput',
        settings={'feature_name': 'x1', 'file_path': csv_path}
    )
    id2 = gsb.add_layer(
        'DeepLearningFC',
        settings={'n_neurons': 1}
    )
    id3 = gsb.add_layer(
        'IoOutput',
        settings={'feature_name': 'y1', 'file_path': csv_path}
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


@pytest.mark.tf2x
def test_progress_reaches_one(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    assert trainer.progress == 0.0 and trainer.num_epochs_completed == 0
    trainer.run()
    assert trainer.progress == 1.0 and trainer.num_epochs_completed == trainer.num_epochs
    

@pytest.mark.tf2x
def test_trainer_has_all_statuses(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)

    seen_statuses = [trainer.status]

    result = None    
    sentinel = object()
    iterator = trainer.run_stepwise()
    
    while result != sentinel:
        result = next(iterator, sentinel)

        if trainer.status not in seen_statuses:
            seen_statuses.append(trainer.status)

    assert seen_statuses == ['Waiting', 'Training', 'Validation', 'Finished']
    
    
@pytest.mark.tf2x
def test_num_completed_batches_are_ok(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    trainer.run()

    # Run some sanity checks
    assert trainer.num_batches_completed_all_epochs == trainer.num_batches_all_epochs
    assert trainer.num_batches_per_epoch*trainer.num_epochs == trainer.num_batches_all_epochs
    assert trainer.num_training_batches_completed_this_epoch > 0
    assert trainer.num_validation_batches_completed_this_epoch > 0
    assert trainer.num_training_batches_completed_this_epoch + trainer.num_validation_batches_completed_this_epoch == trainer.num_batches_completed_this_epoch
    assert trainer.num_batches_completed_this_epoch == trainer.num_batches_per_epoch


@pytest.mark.tf2x
def test_layer_output_ok(script_factory_tf2x, csv_path, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    df = pd.read_csv(csv_path)
    
    expected = df['x1'][0:2].to_numpy()
    actual = trainer.get_layer_output('0')
    
    assert np.all(actual == expected)
    

@pytest.mark.tf2x
def test_layer_weights_is_array(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_weights('1')
    assert isinstance(value, np.ndarray)

@pytest.mark.tf2x
def test_layer_bias_is_array(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_bias('1')
    assert isinstance(value, np.ndarray)
    

@pytest.mark.tf2x
def test_layer_gradients_contain_exactly_one_float(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_weights('1')
    assert isinstance(value, np.ndarray)


@pytest.mark.tf2x
def test_layer_bias_is_array(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    value = trainer.get_layer_bias('1')
    assert isinstance(value, np.ndarray)
    

@pytest.mark.tf2x
def test_layer_gradients_contain_exactly_one_float(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    minimum = trainer.get_layer_gradients('1', 'minimum')
    maximum = trainer.get_layer_gradients('1', 'maximum')
    average = trainer.get_layer_gradients('1', 'average')
    
    assert isinstance(minimum, list) and len(minimum) == 1 and isinstance(minimum[0], np.float32)
    assert isinstance(maximum, list) and len(maximum) == 1 and isinstance(maximum[0], np.float32)
    assert isinstance(average, list) and len(average) == 1 and isinstance(average[0], np.float32)
    assert minimum[0] <= maximum[0]

@pytest.mark.tf2x
def test_layer_gradients_contain_exactly_one_float(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    minimum = trainer.get_layer_gradients('1', 'minimum')
    maximum = trainer.get_layer_gradients('1', 'maximum')
    average = trainer.get_layer_gradients('1', 'average')
    
    assert isinstance(minimum, list) and len(minimum) == 1 and isinstance(minimum[0], np.float32)
    assert isinstance(maximum, list) and len(maximum) == 1 and isinstance(maximum[0], np.float32)
    assert isinstance(average, list) and len(average) == 1 and isinstance(average[0], np.float32)
    assert minimum[0] <= maximum[0]

@pytest.mark.tf2x
def test_computed_results_do_not_change(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    """ Once results have been computed, the Trainer shouldn't modify the structure.

    A simple way to test for that is to pickle the structure twice. 
    Once at the beginning of training and once after.

    Note: the results themselves should change
    """
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)

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

    
@pytest.mark.tf2x    
def test_trainer_inference_model_ok(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    trainer.run()
    model = trainer.get_inference_model()
    x = {'x1': np.array([1.0, 2.0, 3.0])}
    y = model(x)
    assert y['y1'].numpy().shape == (3, 1)
    

@pytest.mark.tf2x
def test_trainer_target_stats_available(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    target_stats = trainer.get_target_stats()
    assert 'y1' in target_stats.sample_batch 

    
@pytest.mark.tf2x
def test_trainer_prediction_stats_available(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    prediction_stats = trainer.get_prediction_stats()
    assert 'y1' in prediction_stats.sample_batch 

    
@pytest.mark.tf2x
def test_trainer_input_stats_available(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps

    input_stats = trainer.get_input_stats()
    assert 'x1' in input_stats.sample_batch 

@pytest.mark.tf2x
def test_trainer_can_pause_and_unpause(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    next(trainer.run_stepwise()) # Take the first training steps
    
    trainer.pause()
    assert trainer.status == 'Paused'

    trainer.unpause()
    assert trainer.status != 'Paused'

@pytest.mark.tf2x
def test_trainer_can_stop(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)

    next(trainer.run_stepwise()) # Take the first training steps    
    trainer.stop()
    assert trainer.status == 'Finished'

@pytest.mark.tf2x
def test_trainer_can_pause_stop(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)

    step = trainer.run_stepwise()
    next(step) # Take the first training steps    
    trainer.pause()
    next(step)
    trainer.stop()
    assert trainer.status == 'Finished'

