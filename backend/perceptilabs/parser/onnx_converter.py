import onnx
import tf2onnx
import tensorflow as tf
import keras2onnx
import sys
import os
from google.protobuf import text_format
from tensorflow.compat.v1.graph_util import convert_variables_to_constants as freeze_graph
from tensorflow.python.platform import gfile


def load_tf2x_model(path):
    return tf.compat.v2.keras.models.load_model(path)

def load_tf1x_model(path):
    f = open(path)
    graph_def = text_format.Parse(f.read(), tf.GraphDef())

    graph = tf.Graph()
    with graph.as_default():
        tf.import_graph_def(graph_def=graph_def, name='')
    return graph

def get_inputs_outputs(path):
    f = open(path)
    graph_def = text_format.Parse(f.read(), tf.GraphDef())
    inputs = list()
    outputs = list()
    name_list = list()
    for node in graph_def.node: # tensorflow.core.framework.node_def_pb2.NodeDef
        name_list.append(node.name)
        inputs.extend(node.input)
    outputs = list(set(name_list) - set(inputs))
    return inputs, outputs

def create_onnx_from_keras(model):
    """Crete an ONNX model from keras and save it to the specified path."""
    onnx_model = keras2onnx.convert_keras(model, 'keras-onnx', debug_mode=1)

    return onnx_model


def load_tf1x_frozen(path):
    with tf.gfile.GFile(path,"rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name = "prefix")
    return graph

def create_onnx_from_tf1x(model):
    """Crete an ONNX model from the tf1x model and save it to the specified path."""
    inputs = [model.as_graph_def().node[0].name + ":0"]
    outputs = [model.as_graph_def().node[-1].name + ":0"]

    onnx_graph = tf2onnx.tfonnx.process_tf_graph(model, 
            continue_on_error=False, verbose=False, target=None,
            opset=None, custom_op_handlers=None,
            custom_rewriter=None, extra_opset=None,
            shape_override=None, inputs_as_nchw=None,
            input_names=inputs, output_names=outputs,
            const_node_values=None)
    model = onnx_graph.make_model("tf1x-onnx")
    return onnx_graph, model

def save_onnx_to_disk(onnx_model, path):
    """Take a generated ONNX model and save it to disk. To be used for export functionality."""
    try:
        with open(path, "wb") as f:
            f.write(onnx_model.SerializeToString())
    except:
        return Exception("Couldn't save the ONNX model to disk!")

if __name__ == "__main__":
    # path = '/Users/adilsalhotra/developer/test/parser/mobilenet_v1_1.0_224/mobilenet_v1_1.0_224_eval.pbtxt'
    path_frozen = '/Users/adilsalhotra/developer/perceptilabs/backend/perceptilabs/parser/mobilenet_v1_1.0_224/mobilenet_v1_1.0_224_frozen.pb'
    # path = '/Users/adilsalhotra/developer/test/parser/nn/saved_model.pb'
    path_frozen1 = '/Users/adilsalhotra/developer/test/file_config/saved_model/saved_model_frozen.pb'
    path = '/Users/adilsalhotra/developer/test/file_config/saved_model/saved_model.pb'

    model = load_tf1x_frozen(path_frozen1)
    test_ = load_tf1x_frozen(path_frozen)

    # graph = load_tf1x_model('/Users/adilsalhotra/developer/test/file_config/saved_model/saved_model.pb')
    onnx_graph, onnx_model = create_onnx_from_tf1x(model)
    save_onnx_to_disk(onnx_model, "reshape_model.onnx")
    print("ONNX model created.")
