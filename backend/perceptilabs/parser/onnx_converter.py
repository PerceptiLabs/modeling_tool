import onnx
import tf2onnx
import tensorflow as tf
import keras2onnx
import sys
import os
from google.protobuf import text_format



def load_tf2x_model(path):
    return tf.compat.v2.keras.models.load_model(path)

def load_tf1x_model(path):
    f = open(path)
    graph_protobuf = text_format.Parse(f.read(), tf.GraphDef())
    
    graph_clone = tf.Graph()
    with graph_clone.as_default():
        tf.import_graph_def(graph_def=graph_protobuf, name="")
    return graph_clone

def create_onnx_from_keras(model):
    """Crete an ONNX model from keras and save it to the specified path."""
    try:
        onnx_model = keras2onnx.convert_keras(model, 'keras-onnx', debug_mode=1)
    except:
        return None
    else:
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
    try:
        onnx_graph = tf2onnx.tfonnx.process_tf_graph(model, 
            continue_on_error=False, verbose=False, target=None,
            opset=None, custom_op_handlers=None,
            custom_rewriter=None, extra_opset=None,
            shape_override=None, inputs_as_nchw=None,
            input_names=[model.as_graph_def().node[0].name + ":0"], output_names=[model.as_graph_def().node[-1].name + ":0"],
            const_node_values=None)
        onnx_model = onnx_graph.make_model("tf1x-onnx")
    except:
        return None
    else:
        return onnx_model

if __name__ == "__main__":
    # path = '/Users/adilsalhotra/developer/test/parser/mobilenet_v1_1.0_224/mobilenet_v1_1.0_224_eval.pbtxt'
    # path_frozen = '/Users/adilsalhotra/developer/test/parser/mobilenet_v1_1.0_224/mobilenet_v1_1.0_224_frozen.pb'


    # model = load_tf1x_frozen(path_frozen)
    # create_onnx_from_tf1x(model, "model.onnx")
    print("ONNX model created.")