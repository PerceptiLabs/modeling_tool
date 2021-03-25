import pytest
from unittest.mock import MagicMock
import os

import numpy as np
import tensorflow as tf


from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.trainregression.spec import TrainRegressionSpec
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.graph.spec import GraphSpec



@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
@pytest.fixture()
def graph_spec(temp_path_100x1, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints,
        os.path.join(temp_path_100x1, '100x1_inputs.npy'),
        os.path.join(temp_path_100x1, '100x1_outputs.npy')
    )        
    yield graph_spec


def make_graph_spec(temp_path_checkpoints, inputs_path, targets_path, learning_rate=0.3, checkpoint_path=None, distributed=False):
    # --- CONNECTIONS ---
    conn_inputs_to_fc = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_fc', dst_var='input')
    conn_fc_to_train = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_train', dst_var='predictions')
    
    conn_labels_to_train = LayerConnection(src_id='layer_labels', src_var='output', dst_id='layer_train', dst_var='labels')
    # --- LAYER SPECS ---
    if checkpoint_path is None:
        checkpoint_path = temp_path_checkpoints
        
    layer_inputs = DataDataSpec(
        id_='layer_inputs',
        name='layer_inputs',
        sources=[DataSource(
            type_='file',
            path=inputs_path,
            ext='.npy',
            split=(70, 20, 10)            
        )],
        checkpoint_path=checkpoint_path,
        forward_connections=(conn_inputs_to_fc,)
    )
    layer_fc = DeepLearningFcSpec(
        id_='layer_fc',
        name='layer_fc',        
        n_neurons=1,
        checkpoint_path = checkpoint_path,
        backward_connections=(conn_inputs_to_fc,),
        forward_connections=(conn_fc_to_train,)
    )
    layer_labels = DataDataSpec(
        id_='layer_labels',
        name='layer_labels',
        sources=[DataSource(
            type_='file',
            path=targets_path,
            ext='.npy',
            split=(70, 20, 10)            
        )],
        checkpoint_path=checkpoint_path,
        forward_connections=(conn_labels_to_train,)
    )
    layer_train = TrainRegressionSpec(
        id_='layer_train',
        name='layer_train',
        batch_size=8,
        learning_rate=learning_rate,
        n_epochs=200,
        checkpoint_path=checkpoint_path,
        backward_connections=(conn_labels_to_train, conn_fc_to_train),
        connection_labels=conn_labels_to_train,
        connection_predictions=conn_fc_to_train,
        optimizer='SGD'
    )

    graph_spec = GraphSpec([
        layer_inputs,
        layer_fc,
        layer_labels,
        layer_train
    ])
    return graph_spec


@pytest.mark.pre_datawizard            
def test_syntax(script_factory):
    layer_spec = TrainRegressionSpec(
        id_='layer_id',
        name='layer_name',
    )
    
    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name = '123'

    try:
        code = LayerHelper(
            script_factory,
            layer_spec,
            graph_spec=graph_spec
        ).get_code(check_syntax=True)
    except SyntaxError as e:
        pytest.fail("Raised syntax error: " + repr(e))
        raise
    

@pytest.mark.pre_datawizard                
def test_can_instantiate(script_factory):
    layer_spec = TrainRegressionSpec(
        id_='layer_id',
        name='layer_name',
        backward_connections=(
            LayerConnection(dst_var='predictions'),
            LayerConnection(dst_var='labels')
        )
    )
    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name = '123'
    
    try:
        code = LayerHelper(
            script_factory,
            layer_spec,
            graph_spec=graph_spec
        ).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))


@pytest.mark.pre_datawizard                    
def test_can_yield(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)

    try:
        next(graph.run())        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))


@pytest.mark.pre_datawizard                    
def test_convergence(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None
    converged = False
    
    loss_list = []
    r_squared_list = []
    while result is not sentinel and not converged:
        result = next(iterator, sentinel)
        loss_list.append(training_layer.loss_training)
        r_squared_list.append(training_layer.r_squared_training)
        if len(loss_list) > 100:
            if((np.mean(np.diff(loss_list) < 0))) and (r_squared_list[-1] > 0 and r_squared_list[-1] <= 1):
                converged = True
            else:
                converged = False
            
    assert converged

    
@pytest.mark.pre_datawizard            
def test_save_model(script_factory, graph_spec, temp_path_100x1):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)    

    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 

    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path_100x1, '1', 'saved_model.pb')
    assert not os.path.isfile(target_path)
    
    training_layer.on_export(temp_path_100x1, mode='TFModel')
    assert os.path.isfile(target_path)  


@pytest.mark.pre_datawizard                
def test_save_checkpoint(script_factory, graph_spec, temp_path_100x1):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
        
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(temp_path_100x1))
    
    training_layer.on_export(temp_path_100x1, mode='checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(temp_path_100x1))

    
@pytest.mark.skip
@pytest.mark.pre_datawizard            
def test_initial_weights_differ(script_factory, temp_path_100x1, temp_path_checkpoints):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(temp_path_100x1, '100x1_inputs.npy')
    targets_path = os.path.join(temp_path_100x1, '100x1_outputs.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode='training') 
    next(iterator)
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))
    
    # --- Create a second graph ---
    graph_spec2 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)

    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2, mode='training') 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    
    assert np.all(w1 != w2)


@pytest.mark.pre_datawizard                
def test_load_checkpoint(script_factory, temp_path_100x1, temp_path_checkpoints):
    inputs_path = os.path.join(temp_path_100x1, '100x1_inputs.npy')
    targets_path = os.path.join(temp_path_100x1, '100x1_outputs.npy')
    
    checkpoint_path = os.path.join(temp_path_100x1, "checkpoint")
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
        learning_rate=0.0
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode='training') 

    for i in range(3):
        next(iterator) # Run a few iterations
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))
    
    tl1.on_export(checkpoint_path, mode='checkpoint')
    
    # --- Create a second graph and restore the checkpoint ---
    graph_spec2 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
        checkpoint_path=checkpoint_path,
        learning_rate=0.0
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2, mode='training') 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))

    assert np.all(w1 == w2)
