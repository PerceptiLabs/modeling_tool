import pytest
import os
import tensorflow as tf
import pkg_resources
import numpy as np
import shutil

from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE, TOP_LEVEL_IMPORTS, TOP_LEVEL_IMPORTS_FLAT
from perceptilabs.core_new.graph.builder import GraphBuilder


def fix_path(x):
    return x.replace('\\', '/')


@pytest.fixture(autouse=True)
def reset():
    yield
    tf.reset_default_graph()
    

@pytest.fixture(scope='module')
def j2_engine():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory, verbose=True)
    yield j2_engine


@pytest.fixture(scope='function')
def tmpdir_del(tmpdir):
    yield fix_path(str(tmpdir))
    shutil.rmtree(tmpdir)
    
@pytest.fixture(scope='function')
def layer_fc(j2_engine):
    layer_fc_ = create_layer(
        j2_engine,
        DEFINITION_TABLE, TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DeepLearningFC',
        # top_level_imports=TOP_LEVEL_IMPORTS_FLAT[0],
        n_neurons=3,
        activation='',
        dropout=False
    )
    yield layer_fc_

@pytest.fixture(scope='function')
def layer_inputs(j2_engine, tmpdir_del):
    mat_inputs = np.array(
        [
            [0.1, 0.2, 0.3, 1.0],        
    
        ]*200
    )
    inputs_path = fix_path(os.path.join(tmpdir_del, 'inputs.npy'))
    np.save(inputs_path, mat_inputs)
    imports = []
    imports.append(TOP_LEVEL_IMPORTS_FLAT)
    layer_inputs_ = create_layer(
        j2_engine, DEFINITION_TABLE,TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DataData',

        sources=[{'type': 'file', 'ext':'.npy', 'path': inputs_path}],
        partitions=[(100, 0, 0)],
    )

    yield layer_inputs_
    #shutil.rmtree(tmpdir_del)


@pytest.fixture(scope='function')
def layer_targets(j2_engine, tmpdir_del):
    mat_targets = np.array(
        [
            [1, 0, 0],        
        ]*200
    )
    targets_path = fix_path(os.path.join(tmpdir_del, 'targets.npy'))
    np.save(targets_path, mat_targets)

    layer_targets_ = create_layer(
        j2_engine, DEFINITION_TABLE,TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DataData',
        sources=[{'type': 'file', 'ext':'.npy',  'path': targets_path}],
        partitions=[(100, 0, 0)],
    )

    yield layer_targets_



def make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc, export_dir=None, distributed=False, learning_rate=0.3, n_epochs=200):
    imports = []
    imports.append(TOP_LEVEL_IMPORTS_FLAT)
    layer_training = create_layer(
        j2_engine,
        DEFINITION_TABLE,TOP_LEVEL_IMPORTS_FLAT,
        layer_type='TrainRegression',
        output_layer='layer_fc',
        # top_level_imports=TOP_LEVEL_IMPORTS_FLAT,
        target_layer='layer_targets',
        n_epochs=n_epochs,
        #TODO: The loss function doesn't do anything. You can put any string and the code will work. Should be fixed
        loss_function='Mean Absolute Error',
        class_weights='1',
        optimizer='tf.compat.v1.train.GradientDescentOptimizer',
        learning_rate=learning_rate,
        decay_steps=100000,
        decay_rate=0.96,
        momentum=0.9,
        beta1=0.9,
        batch_size=10,
        distributed=distributed,
        export_directory=export_dir
    )
    
    layers = {
        'layer_inputs': layer_inputs,
        'layer_fc': layer_fc,        
        'layer_targets': layer_targets,
        'layer_training': layer_training # TODO: Placeholder for training layer. Should probably be redesigned to not include training layer.                
    }

    edges = [
        ('layer_inputs', 'layer_fc'),
        ('layer_fc', 'layer_training'),
        ('layer_targets', 'layer_training'),                
    ]
    
    graph_builder = GraphBuilder()
    graph = graph_builder.build(layers, edges)    
    return graph

@pytest.mark.slow
def test_convergence(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc):
    graph = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!


    sentinel = object()
    result = None
    converged = False
    
    loss_list = []
    r_squared_list = []
    while result is not sentinel and not converged:
        result = next(iterator, sentinel)

        loss_list.append(training_layer.loss_training)
        r_squared_list.append(training_layer.r_squared_training)
        
        # If the loss is not going down, then we are not converging, so return false!
        if len(loss_list) > 100:
            if((np.mean(np.diff(loss_list) < 0))) and (r_squared_list[-1] > 0 and r_squared_list[-1] <= 1):
                converged = True
            else:
                converged = False
            
    assert converged

def test_save_model(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc):
    graph = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. shouldnt be!
    next(iterator) # First iteration (including initialization)
    assert not os.path.isfile(fix_path(os.path.join(tmpdir_del, '1', 'saved_model.pb')))
    
    training_layer.on_export(tmpdir_del, mode='TFModel')
    assert os.path.isfile(fix_path(os.path.join(tmpdir_del, '1', 'saved_model.pb')))

def test_save_checkpoint(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc):
    graph = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, layer_fc)
    
    training_layer = graph.active_training_node.layer
    iterator = training_layer.run(graph) # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(tmpdir_del))
    
    training_layer.on_export(tmpdir_del, mode='TFModel+checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(tmpdir_del))

def test_initial_weights_differ(j2_engine, tmpdir_del, layer_inputs, layer_targets):
    # --- Create a graph ---    
    fc1 = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        layer_type='DeepLearningFC',
        top_level_imports=TOP_LEVEL_IMPORTS_FLAT,
        n_neurons=3,
        activation='',
        dropout=False, keep_prob=1.0
    )
    
    graph1 = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, fc1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!
    next(iterator)
    
    w1 = next(iter(tl1.layer_weights['layer_fc'].values()))


    # --- Create a second graph ---
    fc2 = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        top_level_imports=TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DeepLearningFC',
        n_neurons=3,
        activation='',
        dropout=False, keep_prob=1.0
    )
    graph2 = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, fc2) 
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) 

    # TODO: set learning rate to zero in the second graph to verify that weights are identical.    
    w2 = next(iter(tl2.layer_weights['layer_fc'].values()))

    assert np.all(w1 != w2)

def test_load_checkpoint(j2_engine, tmpdir_del, layer_inputs, layer_targets):

    # --- Create a graph, do some training and save a checkpoint ---    
    fc1 = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        top_level_imports=TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DeepLearningFC',
        n_neurons=3,
        activation='',
        dropout=False, keep_prob=1.0
    )
    
    graph1 = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, fc1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1) # TODO: self reference is weird. design flaw!

    for i in range(3):
        next(iterator) # Run a few iterations
    w1 = next(iter(tl1.layer_weights['layer_fc'].values()))

    tl1.on_export(tmpdir_del, mode='TFModel+checkpoint')

    # --- Create a second graph and restore the checkpoint ---
    fc2 = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        top_level_imports=TOP_LEVEL_IMPORTS_FLAT,
        layer_type='DeepLearningFC',
        n_neurons=3,
        activation='',
        dropout=False, keep_prob=1.0
    )
    graph2 = make_graph(j2_engine, tmpdir_del, layer_inputs, layer_targets, fc2, export_dir=str(tmpdir_del), learning_rate=0.0) 
    
    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2) 
    next(iterator) # Since learning rate is zero, the training step will NOT change the weights. Thus they should remain equal to the checkpoint values.

    # TODO: set learning rate to zero in the second graph to verify that weights are identical.    
    w2 = next(iter(tl2.layer_weights['layer_fc'].values()))

    assert np.all(w1 == w2)