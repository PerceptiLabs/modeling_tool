# from parse_onnx import LayerCheckpoint, get_layer, parse, convert_checkpoint, get_names
from parse_onnx import Parser
from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.specbase import LayerConnection
from onnx_converter import create_onnx_from_tf1x, load_tf1x_model, load_tf1x_frozen
import pytest
import tensorflow as tf
import os
import onnx
from onnx import helper
from onnx import AttributeProto, TensorProto, GraphProto

INPUT_SHAPE = [784,]
TARGET_SHAPE = [28,28,1]

def test_convert_reshape_onnx():
    X = helper.make_tensor_value_info('X', TensorProto.FLOAT, INPUT_SHAPE)
    Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, TARGET_SHAPE)
    assert X is not None and Y is not None

    node_def = helper.make_node('Reshape', ['X'], ['Y'])

    # Create the graph (GraphProto)
    graph_def = helper.make_graph([node_def],'test-model',[X],[Y])

    # Create the ONNX model
    onnx_model = helper.make_model(graph_def, producer_name='onnx-example')

    layer_spec = Parser(onnx_model).parse()[-1]
    assert list(layer_spec.shape) == TARGET_SHAPE

def test_convert_reshape_tf1x():
    onnx_model = None
    with tf.compat.v1.Session() as sess:
        x = tf.compat.v1.placeholder(tf.float32, INPUT_SHAPE, name="input")
        y = tf.reshape(x, shape=TARGET_SHAPE, name="reshape")
        _ = tf.identity(y, name="output")
        
    
        _, onnx_model = create_onnx_from_tf1x(sess.graph)
        assert onnx_model is not None
    
        layer_spec = Parser(onnx_model).parse()[-1]
        assert list(layer_spec.shape) == TARGET_SHAPE
