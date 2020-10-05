import pytest
from unittest.mock import MagicMock
import os

import numpy as np
import tensorflow as tf

from perceptilabs.utils import add_line_numbering
from perceptilabs.issues import traceback_from_exception
from perceptilabs.script import ScriptFactory
from perceptilabs.layers.helper import LayerHelper
from perceptilabs.layers.trainobjectdetection.spec import TrainObjectDetectionSpec
from perceptilabs.layers.datadata.spec import DataDataSpec, DataSource
from perceptilabs.layers.specbase import LayerConnection
from perceptilabs.layers.processrescale.spec import ProcessRescaleSpec
from perceptilabs.layers.deeplearningconv.spec import DeepLearningConvSpec
from perceptilabs.layers.utils import graph_spec_to_core_graph
from perceptilabs.graph.spec import GraphSpec



@pytest.fixture(scope='module')
def script_factory():
    yield ScriptFactory()


def test_syntax(script_factory):
    layer_spec = TrainObjectDetectionSpec(
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
    

def test_can_instantiate(script_factory):
    layer_spec = TrainObjectDetectionSpec(
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
        instance = LayerHelper(
            script_factory,
            layer_spec,
            graph_spec=graph_spec
        ).get_instance()
    except Exception as e:
        pytest.fail("Raised error on instantiation! " + repr(e))



def test_can_yield(script_factory, tutorial_data_path):
    # --- CONNECTIONS ---
    conn_inputs_to_rescale = LayerConnection(src_id='layer_inputs', src_var='output', dst_id='layer_rescale', dst_var='input')
    conn_rescale_to_conv = LayerConnection(src_id='layer_rescale', src_var='output', dst_id='layer_conv', dst_var='input')
    conn_conv_to_train = LayerConnection(src_id='layer_conv', src_var='output', dst_id='layer_train', dst_var='predictions')
    
    conn_labels_to_train = LayerConnection(src_id='layer_labels', src_var='output', dst_id='layer_train', dst_var='labels')

    # --- LAYER SPECS ---
    layer_inputs = DataDataSpec(
        id_='layer_inputs',
        name='layer_inputs',
        sources=[DataSource(
            type_='file',
            path=os.path.join(tutorial_data_path, 'object_detection_input.npy'),
            ext='.npy',
            split=(70, 20, 10)            
        )],
        forward_connections=(conn_inputs_to_rescale,)
    )
    layer_rescale = ProcessRescaleSpec(
        id_='layer_rescale',
        name='layer_rescale',
        width=7,
        height=7,
        backward_connections=(conn_inputs_to_rescale,),
        forward_connections=(conn_rescale_to_conv,)
    )
    layer_conv = DeepLearningConvSpec(
        id_='layer_conv',
        name='layer_conv',
        patch_size=1,
        stride=1,
        padding='SAME',
        feature_maps=13,
        backward_connections=(conn_rescale_to_conv,),
        forward_connections=(conn_conv_to_train,)
    )
    layer_labels = DataDataSpec(
        id_='layer_labels',
        name='layer_labels',
        sources=[DataSource(
            type_='file',
            path=os.path.join(tutorial_data_path, 'object_detection_labels.npy'),
            ext='.npy',
            split=(70, 20, 10)            
        )],
        forward_connections=(conn_labels_to_train,)
    )
    layer_train = TrainObjectDetectionSpec(
        id_='layer_train',
        name='layer_train',
        backward_connections=(conn_labels_to_train, conn_conv_to_train),
        connection_labels=conn_labels_to_train,
        connection_predictions=conn_conv_to_train
    )

    graph_spec = GraphSpec([
        layer_inputs,
        layer_rescale,
        layer_conv,
        layer_labels,
        layer_train
    ])

    graph = graph_spec_to_core_graph(script_factory, graph_spec)
    
    try:
        next(graph.run())        
    except Exception as e:
        pytest.fail("Raised error on run!\n" + traceback_from_exception(e))



        
