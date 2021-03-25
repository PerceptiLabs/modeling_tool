import pytest

import numpy as np
import tensorflow as tf


from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.trainreinforce.spec import TrainReinforceSpec
from perceptilabs.layers.dataenvironment.spec import DataEnvironmentSpec
from perceptilabs.layers.processgrayscale.spec import ProcessGrayscaleSpec
from perceptilabs.layers.deeplearningfc.spec import DeepLearningFcSpec
from perceptilabs.layers.deeplearningrecurrent.spec import DeepLearningRecurrentSpec
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.graph.spec import GraphSpec


@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


@pytest.mark.pre_datawizard                
def test_syntax(script_factory):
    layer_spec = TrainReinforceSpec(
        id_='layer_id',
        name='layer_name',
    )
    try:
        code = LayerHelper(script_factory, layer_spec).get_code(check_syntax=True)
    except SyntaxError:
        pytest.fail("Raised syntax error!")
    

@pytest.mark.pre_datawizard                    
def test_can_instantiate(script_factory):
    layer_spec = TrainReinforceSpec(
        id_='layer_id',
        name='layer_name',
    )
    try:
        instance = LayerHelper(script_factory, layer_spec).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))
    

@pytest.mark.pre_datawizard                    
def test_can_yield(script_factory, tutorial_data_path):
    # --- CONNECTIONS ---
    conn_inputs_to_grayscale = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_grayscale', dst_var='input')
    conn_grayscale_to_fc = LayerConnection(src_id='layer_grayscale', src_var='output', dst_id='layer_fc', dst_var='input')
    conn_fc_to_train = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_train', dst_var='action')

    # --- LAYER SPECS ---
    layer_inputs = DataEnvironmentSpec(
        id_='layer_inputs',
        name='layer_inputs',
        forward_connections=(conn_inputs_to_grayscale,)
    )
    layer_grayscale = ProcessGrayscaleSpec(
        id_='layer_grayscale',
        name='layer_grayscale',
        backward_connections=(conn_inputs_to_grayscale,),
        forward_connections=(conn_grayscale_to_fc,)
    )
    layer_fc = DeepLearningFcSpec(
        id_='layer_fc',
        name='layer_fc',        
        n_neurons=4,
        backward_connections=(conn_grayscale_to_fc,),
        forward_connections=(conn_fc_to_train,)
    )
    layer_train = TrainReinforceSpec(
        id_='layer_train',
        name='layer_train',
        batch_size=2,
        final_exploration_frame=1,
        backward_connections=(conn_fc_to_train,),
    )

    graph_spec = GraphSpec([
        layer_inputs,
        layer_grayscale,
        layer_fc,
        layer_train
    ])

    graph = graph_spec_to_core_graph(script_factory, graph_spec)

    try:
        iterator = graph.run()
        for i in range(10):
            next(iterator)        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))


# NOTE: Testing the unity environment involves loading a unity environment object and running an iteration of it, which opens up the 
# unity env in a separate window. This would in all likelihood cause the build pipeline to fail in any pull request, so for now, skip 
# any unit tests relating to unity.
@pytest.mark.skip
@pytest.mark.pre_datawizard            
def test_can_yield_unity_basic(script_factory, tutorial_data_path):
    # --- CONNECTIONS ---
    conn_inputs_to_fc = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_fc', dst_var='input')
    conn_fc_to_train = LayerConnection(src_id='layer_fc', src_var='output', dst_id='layer_train', dst_var='input')


    # --- LAYER SPECS ---
    layer_inputs = DataEnvironmentSpec(
        id_='layer_inputs',
        name='layer_inputs',
        use_unity=True,
        environment_name='Basic',
        forward_connections=(conn_inputs_to_fc,)
    )
    layer_fc = DeepLearningFcSpec(
        id_='layer_fc',
        name='layer_fc',        
        n_neurons=4,
        backward_connections=(conn_inputs_to_fc,),
        forward_connections=(conn_fc_to_train,)
    )
    layer_train = TrainReinforceSpec(
        id_='layer_train',
        name='layer_train',
        batch_size=2,
        final_exploration_frame=1,
        backward_connections=(conn_fc_to_train,),
    )

    graph_spec = GraphSpec([
        layer_inputs,
        layer_fc,
        layer_train
    ])

    graph = graph_spec_to_core_graph(script_factory, graph_spec)

    try:
        iterator = graph.run()       
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))
