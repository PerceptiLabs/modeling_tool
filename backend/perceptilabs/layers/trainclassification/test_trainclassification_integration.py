import pytest
from unittest.mock import MagicMock
import os
import shutil
import numpy as np
import tensorflow as tf


from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.trainclassification.spec import TrainClassificationSpec
from perceptilabs.graph.spec import GraphSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

    
@pytest.fixture(scope='module')
def script_factory_tf2x():
    yield ScriptFactory(mode='tf2x')
    
@pytest.fixture()
def graph_spec(make_graph_spec, temp_path, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints, 
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy')
    )        
    yield graph_spec

    
@pytest.fixture()
def graph_spec_early_stopping(make_graph_spec, temp_path, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints, 
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy'),
        early_stopping=True        
    )        
    yield graph_spec

    
@pytest.fixture()
def graph_spec_few_epochs(make_graph_spec, temp_path, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints, 
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy'),
        n_epochs=5,
        load_checkpoint=False
    )        
    yield graph_spec
    
    
@pytest.fixture()
def graph_spec_distr(make_graph_spec, temp_path, temp_path_checkpoints):
    graph_spec = make_graph_spec(
        temp_path_checkpoints,
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy'),
        distributed=True
    )        
    yield graph_spec


@pytest.mark.pre_datawizard                
def test_syntax(script_factory):
    layer_spec = TrainClassificationSpec(
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
    layer_spec = TrainClassificationSpec(
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
def test_get_prediction_data_layer(script_factory, graph_spec):
    training_layer = graph_spec.training_layer        
    actual = training_layer.get_prediction_data_layer(graph_spec)
    expected = graph_spec.layers[0] # input data layer
    assert actual == expected

    
@pytest.mark.pre_datawizard                
def test_get_target_data_layer(script_factory, graph_spec):
    training_layer = graph_spec.training_layer    
    actual = training_layer.get_target_data_layer(graph_spec)
    expected = graph_spec.layers[2] # labels data layer
    assert actual == expected


@pytest.mark.pre_datawizard                
def test_get_prediction_inner_layers(script_factory, graph_spec):
    training_layer = graph_spec.training_layer
    actual = training_layer.get_prediction_inner_layers(graph_spec)
    expected = [graph_spec.layers[1]]
    assert actual == expected

    
@pytest.mark.pre_datawizard            
def test_get_target_inner_layers(script_factory, graph_spec):
    training_layer = graph_spec.training_layer    
    actual = training_layer.get_target_inner_layers(graph_spec)
    expected = []
    assert actual == expected
    

@pytest.mark.pre_datawizard    
def test_can_yield(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)

    try:
        next(graph.run(mode = 'training'))        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))

    #tf.reset_default_graph()


@pytest.mark.pre_datawizard        
def test_convergence(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. shouldnt be!

    sentinel = object()
    result = None
    converged = False
    
    accuracy_list = []
    while result is not sentinel and not converged:
        result = next(iterator, sentinel)

        accuracy_list.append(training_layer.accuracy_training)
        if np.mean(accuracy_list[-10:]) >= 0.8:
            converged = True
            
    assert converged

    
@pytest.mark.pre_datawizard        
def test_save_model(script_factory, graph_spec, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)    

    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. shouldnt be!

    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path, '1', 'saved_model.pb')
    assert not os.path.isfile(target_path)
    
    training_layer.on_export(temp_path, mode='TFModel')
    assert os.path.isfile(target_path)
    #tf.reset_default_graph()    

    
@pytest.mark.pre_datawizard        
def test_save_checkpoint(script_factory, graph_spec, temp_path_checkpoints):
    checkpoint_path = temp_path_checkpoints
    os.makedirs(checkpoint_path, exist_ok=True)
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
        
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(checkpoint_path))

    training_layer.on_export(checkpoint_path, mode='checkpoint')
    
    assert any(x.startswith('model.ckpt') for x in os.listdir(checkpoint_path))
    #tf.reset_default_graph()
    shutil.rmtree(checkpoint_path)

    
@pytest.mark.skip
@pytest.mark.pre_datawizard    
def test_initial_weights_differ(make_graph_spec, script_factory, temp_path, temp_path_checkpoints):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!
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
    iterator = tl2.run(graph2, mode = 'training') 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    assert np.all(w1 != w2)
    

@pytest.mark.pre_datawizard        
def test_load_checkpoint(make_graph_spec, script_factory, temp_path, temp_path_checkpoints):
    checkpoint_path = os.path.join(temp_path, "checkpoint")
    
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!

    for i in range(3):
        next(iterator) # Run a few iterations
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))

    tl1.on_export(checkpoint_path, mode='checkpoint')
    # tf.reset_default_graph()
    
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
    iterator = tl2.run(graph2, mode = 'training') 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    assert np.all(w1 == w2)
    
@pytest.mark.pre_datawizard    
def test_syntax_distributed(script_factory):
    layer_spec = TrainClassificationSpec(
        id_='layer_id',
        name='layer_name',
        distributed=True
    )
    
    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name = '123'

    try:
        code = LayerHelper(
            script_factory,
            layer_spec,
            graph_spec=graph_spec,
        ).get_code(check_syntax=True)
    except SyntaxError as e:
        pytest.fail("Raised syntax error: " + repr(e))
        raise
    #tf.reset_default_graph()


@pytest.mark.pre_datawizard        
def test_can_instantiate_distributed(script_factory):
    layer_spec = TrainClassificationSpec(
        id_='layer_id',
        name='layer_name',
        distributed=True,
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
    #tf.reset_default_graph()


@pytest.mark.pre_datawizard            
def test_can_yield_distributed(script_factory, graph_spec_distr):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)

    try:
        next(graph.run(mode = 'training'))        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))
    #tf.reset_default_graph()


@pytest.mark.pre_datawizard        
def test_convergence_distributed(script_factory, graph_spec_distr):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. shouldnt be!

    sentinel = object()
    result = None
    converged = False

    accuracy_list = []
    while result is not sentinel and not converged:
        result = next(iterator, sentinel)
        
        accuracy_list.append(training_layer.accuracy_training)
        if np.mean(accuracy_list[-10:]) >= 0.8:
            converged = True

    assert converged

    
@pytest.mark.pre_datawizard        
def test_save_model_distributed(script_factory, graph_spec_distr, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)    

    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. shouldnt be!

    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path, '1', 'saved_model.pb')
    assert not os.path.isfile(target_path)    
    
    training_layer.on_export(temp_path, mode='TFModel')
    assert os.path.isfile(target_path)


@pytest.mark.pre_datawizard        
def test_save_checkpoint_distributed(script_factory, graph_spec_distr, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)
        
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(temp_path))
    
    training_layer.on_export(temp_path, mode='checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(temp_path))


@pytest.mark.skip
@pytest.mark.pre_datawizard    
def test_initial_weights_differ_distributed(make_graph_spec, script_factory, temp_path, temp_path_checkpoints):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
        distributed=True
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!
    next(iterator)
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))

    # --- Create a second graph ---
    graph_spec2 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
        distributed=True        
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)

    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2, mode = 'training') 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))

    assert np.all(w1 != w2)


@pytest.mark.pre_datawizard        
def test_load_checkpoint_distributed(make_graph_spec, script_factory, temp_path, temp_path_checkpoints):
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    checkpoint_path = os.path.join(temp_path, 'checkpoints')
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
        targets_path,
        distributed=True
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!

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
        learning_rate=0.0,
        distributed=True
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2, mode = 'training') 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))

    assert np.all(w1 == w2)


def test_can_convert_to_dict_and_back(graph_spec):
    dict_ = graph_spec.to_dict()
    new_spec = GraphSpec.from_dict(dict_)
    dict_1 = new_spec.to_dict()
    assert dict_ == dict_1


def test_tf2x_syntax(script_factory_tf2x):
    layer_spec = TrainClassificationSpec(
        id_='layer_id',
        name='layer_name',
    )
    
    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name.return_value = '123'
    
    try:
        code = LayerHelper(
            script_factory_tf2x,
            layer_spec,
            graph_spec=graph_spec
        ).get_code(check_syntax=True, print_code=True)
    except SyntaxError as e:
        pytest.fail("Raised syntax error: " + repr(e))
        raise
    

def test_tf2x_can_instantiate(script_factory_tf2x):
    layer_spec = TrainClassificationSpec(
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
            script_factory_tf2x,
            layer_spec,
            graph_spec=graph_spec
        ).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))


def test_tf2x_can_yield(script_factory_tf2x, graph_spec):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec, print_code=True)

    try:
        next(graph.run(mode='training'))        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))


def test_tf2x_progress_reaches_status_training(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') 

    sentinel = object()
    result = None
    reached_condition = False
    
    while result is not sentinel and not reached_condition:
        result = next(iterator, sentinel)

        if training_layer.status == 'training':
            reached_condition = True

    assert reached_condition


def test_tf2x_progress_reaches_status_finished(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') 

    sentinel = object()
    result = None
    reached_condition = False
    
    while result is not sentinel and not reached_condition:
        result = next(iterator, sentinel)

        if training_layer.status == 'finished':
            reached_condition = True

    assert reached_condition
    
        

def test_tf2x_progress_reaches_one(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode = 'training') 

    sentinel = object()
    result = None
    reached_one = False
    
    while result is not sentinel and not reached_one:
        result = next(iterator, sentinel)

        if training_layer.progress == 1.0:
            reached_one = True

    assert reached_one

    
def test_tf2x_layer_output_values_set(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None

    values_set = False    
    while result is not sentinel and not values_set:
        result = next(iterator, sentinel)
        values_set = all(len(out_dict) > 0 for out_dict in training_layer.layer_outputs.values())

    assert values_set


def test_tf2x_layer_weights_and_biases_set(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer    
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None

    values_set = False    
    while result is not sentinel and not values_set:
        result = next(iterator, sentinel)

        values_set = (
            isinstance(training_layer.layer_weights[fc_layer_id].get('W'), np.ndarray) and
            isinstance(training_layer.layer_biases[fc_layer_id].get('b'), np.ndarray)
        )

    assert values_set


def test_tf2x_layer_gradients_set(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer    
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None

    values_set = False    
    while result is not sentinel and not values_set:
        result = next(iterator, sentinel)

        values_set = (
            isinstance(training_layer.layer_gradients[fc_layer_id].get('W'), np.ndarray) and
            isinstance(training_layer.layer_gradients[fc_layer_id].get('b'), np.ndarray)
        )

    assert values_set

    
def test_tf2x_layer_metrics_set(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer    
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None

    values_set = False    
    while result is not sentinel and not values_set:
        result = next(iterator, sentinel)
        
        values_set = (
            isinstance(training_layer.loss_training, np.float32) and
            isinstance(training_layer.loss_validation, np.float32) and            
            isinstance(training_layer.accuracy_training, np.float32) and
            isinstance(training_layer.accuracy_validation, np.float32) and            
            0 <= training_layer.accuracy_training <= 1.0 and
            0 <= training_layer.accuracy_validation <= 1.0 
        )

    assert values_set

    
def test_tf2x_convergence(script_factory_tf2x, graph_spec):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec, print_code=True)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None
    converged = False
    
    accuracy_list = []
    while result is not sentinel and not converged:
        result = next(iterator, sentinel)

        accuracy_list.append(training_layer.accuracy_training)
        if np.mean(accuracy_list[-10:]) >= 0.8:
            converged = True
            
    assert converged


def test_tf2x_policy_dict_is_not_empty(script_factory_tf2x, graph_spec):
    from perceptilabs.core_new.policies import policy_classification
    
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec, print_code=True)

    fn_is_paused = lambda: False
    fn_sanitized_to_name = lambda sanitized_name: graph_spec.get_layer_by_sanitized_name(sanitized_name).name
    fn_sanitized_to_id = lambda sanitized_name: graph_spec.get_layer_by_sanitized_name(sanitized_name).id_

    sentinel = object()
    result = None
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training')

    results = {}

    while result is not sentinel and not results:
        result = next(iterator, sentinel)

        results = policy_classification(
            fn_is_paused,
            [graph],
            fn_sanitized_to_name,
            fn_sanitized_to_id,
            results
        )
    assert results
    

def test_tf2x_early_stopping_on_training_accuracy(script_factory_tf2x, graph_spec_early_stopping):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_early_stopping, print_code=True)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph, mode='training') 
    sentinel = object()
    result = None
    
    last_accuracy = None
    while result is not sentinel:
        result = next(iterator, sentinel)
        last_accuracy = training_layer.accuracy_training

    assert (
        100*last_accuracy > graph_spec_early_stopping.training_layer.target_acc and
        training_layer.epoch < graph_spec_early_stopping.training_layer.n_epochs - 1
    )

    
def test_tf2x_layer_auc_set(script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer

    iterator = training_layer.run(graph, mode='training') 

    sentinel = object()
    result = None

    values_set = False    
    while result is not sentinel and not values_set:
        result = next(iterator, sentinel)

        values_set = (
            isinstance(training_layer.auc_training, np.float32) and
            isinstance(training_layer.auc_validation, np.float32) and
            0 <= training_layer.auc_training <= 1.0 and
            0 <= training_layer.auc_validation <= 1.0        
        )

    assert values_set

    
def test_tf2x_export_tfmodel_can_load_and_predict(temp_path, script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer

    iterator = training_layer.run(graph, mode='training') 

    for _ in iterator:
        pass
    
    training_layer.on_export(temp_path, 'TFModel')

    loaded_model = tf.keras.models.load_model(os.path.join(temp_path, '1')) # Adds a subdirectory for model version
    assert isinstance(loaded_model.predict({'output': np.random.random((1, 4))}), np.ndarray)


def test_tf2x_save_weights_automatically(temp_path, script_factory_tf2x, graph_spec_few_epochs):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    
    fc_layer_id = graph.nodes[2].layer_id
    training_layer = graph.active_training_node.layer

    iterator = training_layer.run(graph, mode='training') 

    for _ in iterator:
        pass

    assert any(
        file_name.startswith('model.ckpt')
        for file_name in os.listdir(graph_spec_few_epochs.training_layer.checkpoint_path)
    )


def test_tf2x_load_weights(temp_path, script_factory_tf2x, graph_spec_few_epochs):
    
    def has_equal_weights(tl1, tl2):
        """ Check if two training layers have equal weights """
        for layer_id in tl1.layer_weights.keys():
            for var_name in tl1.layer_weights[layer_id].keys():
                weights1 = tl1.layer_weights[layer_id][var_name]
                weights2 = tl2.layer_weights[layer_id][var_name]                
                if np.any(weights1 != weights2):
                    return False
                
        return True        

    # Train the network once and export the weights 
    graph1 = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    training_layer1 = graph1.active_training_node.layer
    iterator = training_layer1.run(graph1, mode='training') 
    for _ in iterator:
        pass

    # Explicit call to avoid conflict with the call to on_export at the end of training
    checkpoint_dir = os.path.join(temp_path, 'new_ckpt_dir')
    os.mkdir(checkpoint_dir)
    training_layer1.on_export(checkpoint_dir, 'checkpoint')
    
    # Train another network with the same specs
    graph2 = graph_spec_to_core_graph(script_factory_tf2x, graph_spec_few_epochs)
    training_layer2 = graph2.active_training_node.layer
    iterator = training_layer2.run(graph2, mode='training') 
    for _ in iterator:
        pass

    # Assert that the weights are different before loading the checkpoint
    assert not has_equal_weights(training_layer2, training_layer1)

    # Load the checkpoint and compare
    training_layer2.load_weights(checkpoint_dir)
    assert has_equal_weights(training_layer2, training_layer1)


def test_tf2x_test_mode_yields_correct_number_of_outputs(script_factory_tf2x, graph_spec):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec, print_code=True)
    
    n_yields = len(list(graph.run(mode='testing')))
    assert n_yields == 2 # 10% of dataset

    
def test_tf2x_headless_mode_gives_empty_dicts(script_factory_tf2x, graph_spec):
    graph = graph_spec_to_core_graph(script_factory_tf2x, graph_spec)
    
    training_layer = graph.active_training_node.layer    
    iterator = training_layer.run(graph, mode='training') 

    all_dicts_have_content = lambda: (
        training_layer.layer_weights != {},
        training_layer.layer_biases != {},            
        training_layer.layer_gradients != {},
        training_layer.layer_outputs != {}
    )
    all_dicts_are_empty = lambda: (
        training_layer.layer_weights == {},
        training_layer.layer_biases == {},            
        training_layer.layer_gradients == {},
        training_layer.layer_outputs == {}
    )

    # Take the first training step and check for content
    next(iterator) 
    assert all_dicts_have_content

    training_layer.on_headless_activate() 
    assert all_dicts_are_empty

    # Take a training step and check that dicts _remain_ clear
    next(iterator) 
    assert all_dicts_are_empty

    training_layer.on_headless_deactivate()
    
    # Take another training step and check that dicts are populated again
    next(iterator) 
    assert all_dicts_have_content
