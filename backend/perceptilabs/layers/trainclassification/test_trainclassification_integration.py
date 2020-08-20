import pytest
from unittest.mock import MagicMock
import os

import numpy as np
import tensorflow as tf


from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.trainclassification.spec import TrainClassificationSpec
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource
from perceptilabs.layers.processonehot.spec import ProcessOneHotSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.graph.spec import GraphSpec

#@pytest.fixture(autouse=True)
#def reset():
#    yield
#    tf.reset_default_graph()
    

@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def make_graph_spec(inputs_path, targets_path, learning_rate=0.3, checkpoint_path=None, distributed=False):
    # --- CONNECTIONS ---
    conn_inputs_to_fc = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_fc', dst_var='input')
    conn_fc_to_train = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_train', dst_var='predictions')
    
    conn_labels_to_train = LayerConnection(src_id='layer_labels', src_var='output', dst_id='layer_train', dst_var='labels')
    # --- LAYER SPECS ---
    layer_inputs = DataDataSpec(
        id_='layer_inputs',
        name='layer_inputs',
        sources=[DataSource(
            type_='file',
            path=inputs_path.replace('\\','/'),
            ext='.npy',
            split=(100, 0, 0)            
        )],
        forward_connections=(conn_inputs_to_fc,)
    )
    layer_fc = DeepLearningFcSpec(
        id_='layer_fc',
        name='layer_fc',        
        n_neurons=3,
        backward_connections=(conn_inputs_to_fc,),
        forward_connections=(conn_fc_to_train,)
    )
    layer_labels = DataDataSpec(
        id_='layer_labels',
        name='layer_labels',
        sources=[DataSource(
            type_='file',
            path=targets_path.replace('\\','/'),
            ext='.npy',
            split=(100, 0, 0)            
        )],
        forward_connections=(conn_labels_to_train,)
    )
    layer_train = TrainClassificationSpec(
        id_='layer_train',
        name='layer_train',
        batch_size=8,
        learning_rate=learning_rate,
        n_epochs=200,
        distributed=distributed,
        checkpoint_path=checkpoint_path,
        backward_connections=(conn_labels_to_train, conn_fc_to_train),
        connection_labels=conn_labels_to_train,
        connection_predictions=conn_fc_to_train
    )

    graph_spec = GraphSpec([
        layer_inputs,
        layer_fc,
        layer_labels,
        layer_train
    ])
    return graph_spec


@pytest.fixture()
def graph_spec(temp_path):
    graph_spec = make_graph_spec(
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy')
    )        
    yield graph_spec

    
@pytest.fixture()
def graph_spec_distr(temp_path):
    graph_spec = make_graph_spec(
        os.path.join(temp_path, '16x4_inputs.npy'),
        os.path.join(temp_path, '16x4_targets.npy'),
        distributed=True
    )        
    yield graph_spec
    

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
    

def test_can_instantiate(script_factory):
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
        ).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))

        
def test_can_yield(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)

    try:
        next(graph.run())        
    except Exception as e:
        print(add_line_numbering(code['layer_train']))
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))

    #tf.reset_default_graph()
        
def test_convergence(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!

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

    
def test_save_model(script_factory, graph_spec, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)    

    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!

    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path, '1', 'saved_model.pb')
    assert not os.path.isfile(target_path)
    
    training_layer.on_export(temp_path, mode='TFModel')
    assert os.path.isfile(target_path)
    #tf.reset_default_graph()    
    
    
def test_save_checkpoint(script_factory, graph_spec, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
        
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(temp_path))
    
    training_layer.on_export(temp_path, mode='TFModel+checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(temp_path))
    #tf.reset_default_graph()

def test_initial_weights_differ(script_factory, temp_path):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        inputs_path,
        targets_path
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!
    next(iterator)
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    
    # --- Create a second graph ---
    graph_spec2 = make_graph_spec(
        inputs_path,
        targets_path,
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)

    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    
    assert np.all(w1 != w2)
    

def test_load_checkpoint(script_factory, temp_path):
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    graph_spec1 = make_graph_spec(
        inputs_path,
        targets_path
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!

    for i in range(3):
        next(iterator) # Run a few iterations
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))

    tl1.on_export(temp_path, mode='TFModel+checkpoint')
    #tf.reset_default_graph()
    
    # --- Create a second graph and restore the checkpoint ---
    graph_spec2 = make_graph_spec(
        inputs_path,
        targets_path,
        checkpoint_path=temp_path,
        learning_rate=0.0
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    assert np.all(w1 == w2)
    

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
            graph_spec=graph_spec
        ).get_code(check_syntax=True)
    except SyntaxError as e:
        pytest.fail("Raised syntax error: " + repr(e))
        raise
    #tf.reset_default_graph()
    
def test_can_instantiate_distributed(script_factory):
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
            graph_spec=graph_spec
        ).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))
    #tf.reset_default_graph()

    
def test_can_yield_distributed(script_factory, graph_spec_distr):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)

    try:
        next(graph.run())        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))
    #tf.reset_default_graph()

    
def test_convergence_distributed(script_factory, graph_spec_distr):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!

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

    
def test_save_model_distributed(script_factory, graph_spec_distr, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)    

    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!

    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path, '1', 'saved_model.pb')
    assert not os.path.isfile(target_path)    
    
    training_layer.on_export(temp_path, mode='TFModel')
    assert os.path.isfile(target_path)

    
def test_save_checkpoint_distributed(script_factory, graph_spec_distr, temp_path):
    graph = graph_spec_to_core_graph(script_factory, graph_spec_distr)
        
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(temp_path))
    
    training_layer.on_export(temp_path, mode='TFModel+checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(temp_path))


def test_initial_weights_differ_distributed(script_factory, temp_path):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        inputs_path,
        targets_path,
        distributed=True
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!
    next(iterator)
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))

    # --- Create a second graph ---
    graph_spec2 = make_graph_spec(
        inputs_path,
        targets_path,
        distributed=True        
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)

    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))

    assert np.all(w1 != w2)

    
def test_load_checkpoint_distributed(script_factory, temp_path):
    inputs_path = os.path.join(temp_path, '16x4_inputs.npy')
    targets_path = os.path.join(temp_path, '16x4_targets.npy')
    
    graph_spec1 = make_graph_spec(
        inputs_path,
        targets_path,
        distributed=True
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!

    for i in range(3):
        next(iterator) # Run a few iterations
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc'].values()))

    tl1.on_export(temp_path, mode='TFModel+checkpoint')
    
    # --- Create a second graph and restore the checkpoint ---
    graph_spec2 = make_graph_spec(
        inputs_path,
        targets_path,
        checkpoint_path=temp_path,
        learning_rate=0.0,
        distributed=True
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))

    assert np.all(w1 == w2)


def test_can_convert_to_dict_and_back(graph_spec):
    dict_ = graph_spec.to_dict()
    new_spec = GraphSpec.from_dict(dict_)

    assert new_spec == graph_spec
    
