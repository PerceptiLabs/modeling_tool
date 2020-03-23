import pytest
import os
import tensorflow as tf
import pkg_resources
import numpy as np
import shutil

from perceptilabs.core_new.layers.templates.base import J2Engine
from perceptilabs.core_new.layers.templates.utils import instantiate_layer_from_macro, create_layer
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY, DEFINITION_TABLE
from perceptilabs.core_new.graph.builder import GraphBuilder

@pytest.fixture(scope='module')
def j2_engine():
    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)    
    j2_engine = J2Engine(templates_directory)
    yield j2_engine

    
@pytest.fixture(scope='function')
def graph(j2_engine, tmpdir):
    tf.reset_default_graph()
    
    mat_inputs = np.array([
        [0.1, 0.2, 0.3, 0.4],
        [0.1, 0.3, 0.2, 0.5],
        [0.0, 0.1, 0.1, 0.1]
    ])
    inputs_path = os.path.join(tmpdir, 'inputs.npy')
    np.save(inputs_path, mat_inputs)
    
    mat_targets = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])
    targets_path = os.path.join(tmpdir, 'targets.npy')
    np.save(targets_path, mat_targets)

    layer_inputs = create_layer(
        j2_engine, DEFINITION_TABLE,
        'DataData',
        sources=[{'type': 'file', 'path': inputs_path}],
        partitions=[(100, 0, 0)],
    )

    layer_targets = create_layer(
        j2_engine, DEFINITION_TABLE,
        'DataData',
        sources=[{'type': 'file', 'path': targets_path}],
        partitions=[(100, 0, 0)],
    )

    layer_fc = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        'DeepLearningFC',
        n_neurons=3,
        activation='tf.compat.v1.sigmoid',
        dropout=False, keep_prob=1.0
    )

    layer_training = create_layer(
        j2_engine,
        DEFINITION_TABLE,
        'TrainNormal',
        output_layer='layer_fc',
        target_layer='layer_targets',
        n_epochs=5,
        loss_function='Quadratic',
        class_weights='1',
        optimizer='tf.compat.v1.train.GradientDescentOptimizer',
        learning_rate=0.01,
        decay_steps=100000,
        decay_rate=0.96,
        momentum=0.9,
        beta1=0.9,
        distributed=False,
        export_directory=None
    )
    
    layer_training.save_snapshot_and_process_events = lambda graph: None # TODO: use yield instead?
    layer_training.process_events = lambda graph: None    
    
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
    yield graph
    shutil.rmtree(tmpdir)


def test_blabla(graph):

    training_layer = graph.active_training_node.layer
    training_layer.run(graph) # TODO: self reference is weird. shouldnt be!

    
    #import pdb; pdb.set_trace()


    
