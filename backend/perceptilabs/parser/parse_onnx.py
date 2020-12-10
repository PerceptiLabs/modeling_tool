import onnx
import tensorflow as tf
from onnx import shape_inference
from onnx_converter import create_onnx_from_tf1x, load_tf1x_model, load_tf1x_frozen
from perceptilabs import funclib
from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.specbase import LayerConnection
import google.protobuf
from google.protobuf.json_format import MessageToDict


class LayerCheckpoint():
    def __init__(self, name="", ops=None, shape=(), start_node=False, end_node=False, 
                forward_connections=None, backward_connections=None, is_constant=False, constants=None):
        """
            args 
            name: The name of the component 
            ops: Operations associated with the component
            start_node: If True, the node is the beginning of the network
            end_node: If True, the node is the last in the network
            backward_connectiosn: Come from the inputs of the ONNX graph
        """
        self.name = name
        self.ops = ops or list()
        self.shape = shape
        self.start_node = start_node
        self.end_node = end_node
        self.forward_connections = forward_connections or list()
        self.backward_connections = backward_connections or list()
        self.is_constant = is_constant
        self.constants = constants or list()
        
class Parser():

    def __init__(self, model=None):
        """
            args
            model: The ONNX model to parse

            Other fields:
            low_prio_ops: Low priority operations that we should purge from the list of operation-based LayerCheckpoints. 
            low_prio_inputs: Low priority inputs taht we should purge from the list of input-based LayerCheckpoints. 
        """
        self.low_prio_ops = ['Cast', 'Identity']
        self.low_prio_inputs = ['shape:0']
        self.model = model

    def parse(self):
        """
            Get the inputs, layers, and outputs as lists of LayerCheckpoints. Get relevant information for 
            all operation-based layers and convert them into LayerSpecs. The methods parse_input, parse_operations,
            create these lists of LayerCheckpoints, convert_checkpoint changes it into a LayerSpec. 
        """
        inputs = self.parse_input(self.model.graph.input)
        layers = self.parse_operations(self.model.graph.node)
        outputs = self.parse_outputs(self.model.graph.output)
        self.assign_connections(layers, inputs, outputs)
        self.get_shapes(layers, inputs, outputs)

        return self.convert_checkpoint(layers)

    def load_onnx_model(self,path):
        """Load an ONNX model from disk."""
        onnx_model = onnx.load(path)
        return onnx_model

    def convert_shape(self, dimension_list):
        """Helper function to parse through dimensions and convert them to native types."""
        shape = list()
        for i in range(len(dimension_list)):
            shape.append(dimension_list[i].dim_value)
        return shape

    def get_layer(self, layers, name):
        layer_list = list()
        for layer in layers:
            if name in layer.ops:
                layer_list.append(layer)
        
        return layer_list

    def get_shapes(self,layers, inputs, outputs):
        """Assign output shapes to operation-based layers."""
        for layer in layers:
            for output in outputs:
                if output.name in layer.forward_connections:
                    layer.shape = output.shape

    def sanitize_name(self,unsanitized_name, character):
        sanitized_name = unsanitized_name.split(character)[0]
        return sanitized_name

    def parse_input(self, input_nodes):
        inputs = []
        for inp in input_nodes:
            in_shape = self.convert_shape(inp.type.tensor_type.shape.dim)
            if len(in_shape) > 0 and inp.name.split('/')[-1] not in self.low_prio_inputs:
                inputs.append(LayerCheckpoint(name=inp.name, ops=['Input'], shape=in_shape))
        return inputs

    def parse_operations(self, operation_nodes):
        layers = []
        for node in operation_nodes:

            if node.op_type not in self.low_prio_ops:
                layers.append(LayerCheckpoint(name=node.name, ops=[node.op_type]))
        return layers
    
    def parse_outputs(self, output_nodes):
        outputs = []
        for out in output_nodes:
            out_shape = self.convert_shape(out.type.tensor_type.shape.dim)
            if len(out_shape) > 0:
                outputs.append(LayerCheckpoint(name=out.name, ops=['Output'], shape=out_shape))
        return outputs

    def assign_connections(self, layers, inputs, outputs):
        if len(layers) == len(inputs) and len(inputs) == len(outputs):
            for index in range(len(layers)):
                layers[index].backward_connections.append(inputs[index].name)
                layers[index].forward_connections.append(outputs[index].name)

    def convert_checkpoint(self, layers):
        layer_specs = list()
        for layer_checkpoint in layers:
            layer_spec = ProcessReshapeSpec(
                id_='layer_id', #TODO:(adil.s) Don't manually assign layer ID when building a GraphSpec!
                name=layer_checkpoint.name,
                shape=layer_checkpoint.shape,
                permutation=(0, 1)     
            )
            layer_specs.append(layer_spec)

        return layer_specs
