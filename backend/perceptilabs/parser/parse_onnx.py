import onnx
import tensorflow as tf
from onnx import shape_inference
from perceptilabs.parser.onnx_converter import create_onnx_from_tf1x, load_tf1x_model, load_tf1x_frozen
from perceptilabs import funclib
from perceptilabs.graph.spec import GraphSpec 
from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec
from perceptilabs.layers.processreshape.spec import ProcessReshapeSpec
from perceptilabs.layers.specbase import LayerConnection
import google.protobuf
from google.protobuf.json_format import MessageToDict


import numpy as np
import networkx as nx

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

    def __init__(self, model=None, path=None):
        """
            args
            model: The ONNX model to parse

            Other fields:
            low_prio_ops: Low priority operations that we should purge from the list of operation-based LayerCheckpoints. 
            low_prio_inputs: Low priority inputs taht we should purge from the list of input-based LayerCheckpoints. 
        """
        self.low_prio_ops = ['Cast', 'Identity']
        self.low_prio_inputs = ['shape:0']

        if model is not None:
            self.model = model
        else:
            self.model = self.load_onnx_model(path)
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
        layer_specs = []
        for layer_checkpoint in layers:
            layer_spec = ProcessReshapeSpec(
                id_='layer_id', #TODO:(adil.s) Don't manually assign layer ID when building a GraphSpec!
                name=layer_checkpoint.name,
                shape=layer_checkpoint.shape,
                permutation=(0, 1)     
            )
            layer_specs.append(layer_spec)

        return layer_specs

    def create_id_mappings(self, layer_specs):
                
        idList=np.random.sample(range(1, len(layer_specs)+1, len(layer_specs)))
        name2idDict={}
        id2nameDict={}
        for layer_spec in layer_specs:
            Id=str(idList[0])
            name2idDict[Id]=layer_spec.name
            id2nameDict[layer_spec.name]=Id
        return id2nameDict, name2idDict

    def create_nx_graph(self, layer_specs, name2idDict, id2nameDict):
        json = [GraphSpec(layer_specs).to_dict()]

        G=nx.Graph()
        maxWeight=1

        for layer_spec in layer_specs:
            if len(layer_spec.name.split("/")) > maxWeight:
                maxWeight=len(layer_spec.name.split("/"))
    
        for layer_spec in layer_specs:
            if len(layer_spec.forward_connections) < 1:
                G.add_node(name2idDict[layer_spec.name])
                break
            for con in layer_spec.forward_connections:
                next_layer_name = id2nameDict[con]
                layer_namespace = layer_spec.name.split("/")
                next_layer_namespace = next_layer_name.split("/")
                weight=1

                if len(layer_namespace)>len(next_layer_namespace):
                    for i in next_layer_namespace:
                        if i not in layer_namespace:
                            weight=maxWeight - next_layer_namespace.index(i)
                            break
                else:
                    for i in layer_namespace:
                        if i not in next_layer_namespace:
                            weight=maxWeight - layer_namespace.index(i)
                            break
                # print(weight)
                G.add_edge(name2idDict[layer_spec.name],con,weight=weight)
    
        
        positions=nx.kamada_kawai_layout(G,scale=1500,dim=2,weight='weight') 
        flipped_positions={node: (x,-y) for (node, (x,y)) in positions.items()}

        xScale=yScale=1.3
        minX=50
        minY=50
        for Id,pos in flipped_positions.items():
            if pos[0]*xScale < minX:
                minX = pos[0] * xScale
            if pos[1] * yScale < minY:
                minY = pos[1] * yScale
        
        adjX = 50 - minX
        adjY = 50 - minY
        positionsCopy = {}
        for Id,pos in flipped_positions.items():
            positionsCopy[Id] = [pos[0] * xScale + adjX, pos[1] * yScale + adjY]

        positions = positionsCopy
        return positions

    def save_json(self, layer_spec):
        layer_specs = [layer_spec]

        name2idDict, id2nameDict = self.create_id_mappings(layer_specs)
        positions = self.create_nx_graph(layer_specs, name2idDict, id2nameDict)

        #######################################Create layers in correct foramt#######################################
        layer_dict = dict()
        for layer_spec in layer_specs:
            OutputDim = str(layer_spec.shape).replace("(","").replace(")","").replace(", ","x").replace("None","?")
            layer_dict[name2idDict[layer_spec.name]] = {
                "layerId": name2idDict[layer_spec.name],
                "checkpoint": None,
                "endPoints": layer_spec.end_points,
                # "layerName": layerName.split("/")[-1],
                "layerName": layer_spec.name.split('/')[-1],
                "layerType": layer_spec.type_,
                "layerSettings": "",
                "layerCode":{"Output":layer_spec.custom_code},
                "layerNone": False,
                "layerMeta": {
                    # "layerContainerName": ["/".join(layerName.split("/")[0:i]) for i in range(1,len(layerName.split("/")))],
                    "layerBgColor": '',
                    "layerContainerName": '',
                    "isInvisible": False,
                    "isLock": False,
                    "isSelected": False,
                    "position": {
                    # "top": None,
                    # "left": None
                    # "top": random.randint(10,700),
                    # "left": random.randint(10,700)
                    "top":positions[name2idDict[layer_spec.name]][0],
                    "left":positions[name2idDict[layer_spec.name]][1]
                    },
                    "OutputDim": OutputDim,
                    "InputDim": "",
                    "containerDiff": {
                    "top": 0,
                    "left": 0
                    }
                },
                "layerCodeError": None,
                "componentName": layer_spec.type_,
                "connectionOut":layer_spec.forward_connections,
                "connectionIn":layer_spec.backward_connections,
                "connectionArrow": layer_spec.forward_connections,
                "previewVariable":"output"
            }

        ########################################Create Network#####################################################
        Network={
            "network":{
                "networkName":'ReshapeGraph',
                "networkID":"",
                "networkSettings":None,
                "networkMeta": {},
                "networkElementList": layer_dict,
            }
        }

        return Network
                
