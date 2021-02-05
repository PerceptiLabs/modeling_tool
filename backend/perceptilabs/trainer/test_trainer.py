import os
import pytest
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

from perceptilabs.data import DataLoader, FeatureSpec
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.trainer import Trainer


@pytest.fixture()
def csv_path(temp_path):
    file_path = os.path.join(temp_path, 'data.csv')
    df = pd.DataFrame({'x1': [123.0, 24.0, 13.0, 45.0], 'y1': [1.0, 2.0, 3.0, 4.0]})
    df.to_csv(file_path, index=False)    
    yield file_path

    
@pytest.fixture()
def data_loader(csv_path):
    dl = DataLoader.from_csv(
        feature_specs={
            'x1': FeatureSpec('numerical', 'input'),
            'y1': FeatureSpec('numerical', 'output')            
        },
        path=csv_path
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
    assert trainer.num_training_batches_completed_this_epoch + trainer.num_validation_batches_completed_this_epoch == trainer.num_batches_completed_this_epoch
    assert trainer.num_batches_completed_this_epoch == trainer.num_batches_per_epoch


@pytest.mark.tf2x
def test_trainer_tracked_tensor_structs_ok(script_factory_tf2x, data_loader, graph_spec_few_epochs):
    trainer = Trainer(script_factory_tf2x, data_loader, graph_spec_few_epochs)
    
    next(trainer.run_stepwise()) # Take the first training steps

    def has_valid_struct(dict_):
        if not isinstance(dict_, dict):
            return False

        for layer_id, sub_dict in dict_.items():
            if not isinstance(layer_id, str):
                return False
            if not isinstance(sub_dict, dict):
                return False

            for output_name, output_value in sub_dict.items():
                if not isinstance(output_name, str):
                    return False
                
                if not isinstance(output_value, np.ndarray):
                    return False
        return True

    assert has_valid_struct(trainer.layer_outputs)
    assert has_valid_struct(trainer.layer_gradients)
    assert has_valid_struct(trainer.layer_weights)
    assert has_valid_struct(trainer.layer_biases)            
    


