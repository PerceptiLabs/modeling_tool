import pytest
from unittest.mock import MagicMock

import numpy as np
import tensorflow as tf
import os
import tempfile

from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource
from perceptilabs.layers.datarandom.spec import DataRandomSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.mathswitch.spec import MathSwitchSpec
from perceptilabs.layers.traingan.spec import TrainGanSpec
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.graph.spec import GraphSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()

def make_graph_spec(temp_path_checkpoints, tutorial_data_path, learning_rate=0.3, checkpoint_path=None, distributed=False):
    # --- CONNECTIONS ---
    conn_random_to_fc = LayerConnection(src_id='layer_random', src_var='output', dst_id='layer_fc', dst_var='input')
    conn_fc_to_switch = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_switch', dst_var='input2')
        
    conn_real_to_fc3 = LayerConnection(src_id='layer_real', src_var='output', dst_id='layer_fc3', dst_var='input')
    conn_fc3_to_switch = LayerConnection(src_id='layer_fc3', src_var='output', dst_id='layer_switch', dst_var='input1')

    conn_switch_to_fc2 = LayerConnection(src_id='layer_switch', src_var='output', dst_id='layer_fc2', dst_var='input')
    conn_fc2_to_train = LayerConnection(src_id='layer_fc2', src_var='output', dst_id='layer_train', dst_var='input')

    # --- LAYER SPECS ---
    if checkpoint_path is None:
            checkpoint_path = temp_path_checkpoints
    
    layer_random = DataRandomSpec(
        id_='layer_random',
        name='layer_random',
        shape=(100,),
        checkpoint_path = checkpoint_path,
        forward_connections=(conn_random_to_fc,)
    )

    layer_fc = DeepLearningFcSpec(
        id_='layer_fc',
        name='layer_fc',        
        n_neurons=784,
        checkpoint_path = checkpoint_path,
        backward_connections=(conn_random_to_fc,),
        forward_connections=(conn_fc_to_switch,)
    )

    layer_real = DataDataSpec(
        id_='layer_real',
        name='layer_real',
        sources=[DataSource(
            type_='file',
            path=tutorial_data_path.replace('\\','/'),
            ext='.npy',
            split=(70, 20, 10)            
        )],
        checkpoint_path = checkpoint_path,
        forward_connections=(conn_real_to_fc3,)
    )

    layer_fc3 = DeepLearningFcSpec(
        id_='layer_fc3',
        name='layer_fc3',        
        n_neurons=784,
        checkpoint_path = checkpoint_path,
        backward_connections=(conn_real_to_fc3,),
        forward_connections=(conn_fc3_to_switch,)
    )

    layer_switch = MathSwitchSpec(
        id_='layer_switch',
        name='layer_switch',
        selected_var_name='input1',
        checkpoint_path = checkpoint_path,
        backward_connections=(conn_fc3_to_switch,conn_fc_to_switch,),
        forward_connections=(conn_switch_to_fc2,)
    )

    layer_fc2 = DeepLearningFcSpec(
        id_='layer_fc2',
        name='layer_fc2',        
        n_neurons=1,
        checkpoint_path = checkpoint_path,
        backward_connections=(conn_switch_to_fc2,),
        forward_connections=(conn_fc2_to_train,)
    )
    
    layer_train = TrainGanSpec(
        id_='layer_train',
        name='layer_train',
        switch_layer_name='layer_switch',
        real_layer_name='layer_real',
        stop_condition='Accuracy',
        optimizer='SGD',
        target_acc=80,
        checkpoint_path=checkpoint_path,
        backward_connections=(conn_fc2_to_train,),
    )

    graph_spec = GraphSpec([
        layer_real,
        layer_fc,
        layer_random,
        layer_switch,
        layer_fc2,
        layer_fc3,
        layer_train
    ])
    return graph_spec

@pytest.fixture()
def graph_spec(temp_path_checkpoints, tutorial_data_path):
    graph_spec = make_graph_spec(
        temp_path_checkpoints,
        os.path.join(tutorial_data_path, 'gan_mnist.npy').replace('\\','/')
    )        
    yield graph_spec

def test_syntax(script_factory):
    layer_spec = TrainGanSpec(
        id_='layer_id',
        name='layer_name',
    )
    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name = '123'
    graph_spec.__getitem__.sanetized_name = '456'
    
    try:
        code = LayerHelper(
            script_factory,
            layer_spec,
            graph_spec=graph_spec
        ).get_code(check_syntax=True)
    except SyntaxError as e:
        pytest.fail("Raised syntax error: " + repr(e))
    

def test_can_instantiate(script_factory):
    layer_spec = TrainGanSpec(
        id_='layer_id',
        name='layer_name',
        backward_connections=(
            LayerConnection(dst_var='input'),
        )
    )

    graph_spec = MagicMock()
    graph_spec.nodes_by_id.__getitem__.sanitized_name = '123'
    graph_spec.__getitem__.sanetized_name = '456'
    
    try:
        instance = LayerHelper(
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

def test_save_model(script_factory, graph_spec):
    graph = graph_spec_to_core_graph(script_factory, graph_spec)
    import tempfile    
    temp_path = tempfile.mkdtemp().replace('\\', '/')
    training_layer = graph.active_training_node.layer
    
    iterator = training_layer.run(graph, mode = 'training') # TODO: self reference is weird. shouldnt be!
    next(iterator) # First iteration (including initialization)
    target_path = os.path.join(temp_path, '1', 'saved_model.pb')

    # import pytest; pytest.set_trace()
    # assert not os.path.isfile(target_path)
    
    training_layer.on_export(temp_path, mode='TFModel')
    assert os.path.isfile(target_path)

def test_initial_weights_differ(temp_path_checkpoints, script_factory, tutorial_data_path):
    """ Check that the weights are DIFFERENT when creating two graphs. If not, it might not be meaningful to test loading a checkpoint """
    inputs_path = os.path.join(tutorial_data_path, 'gan_mnist.npy')
    
    # --- Create a graph ---
    graph_spec1 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
    )        
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec1)
    
    tl1 = graph1.active_training_node.layer
    iterator = tl1.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!
    next(iterator)
    w1 = next(iter(tl1.layer_weights['DeepLearningFC_layer_fc2'].values()))
    #tf.reset_default_graph()
    
    # --- Create a second graph ---
    graph_spec2 = make_graph_spec(
        temp_path_checkpoints,
        inputs_path,
    )        
    graph2 = graph_spec_to_core_graph(script_factory, graph_spec2)

    tl2 = graph2.active_training_node.layer
    iterator = tl2.run(graph2, mode = 'training') 
    next(iterator) 
    w2 = next(iter(tl2.layer_weights['DeepLearningFC_layer_fc'].values()))
    #tf.reset_default_graph()
    
    assert np.all(w1 != w2)


def test_save_checkpoint(script_factory, graph_spec):
    temp_path = tempfile.mkdtemp().replace('\\', '/')
    graph1 = graph_spec_to_core_graph(script_factory, graph_spec)

    training_layer = graph1.active_training_node.layer
    iterator = training_layer.run(graph1, mode = 'training') # TODO: self reference is weird. design flaw!

    next(iterator) # First iteration (including initialization)
    assert not any(x.startswith('model.ckpt') for x in os.listdir(temp_path))

    training_layer.on_export(temp_path, mode='checkpoint')
    assert any(x.startswith('model.ckpt') for x in os.listdir(temp_path))
    #tf.reset_default_graph()

