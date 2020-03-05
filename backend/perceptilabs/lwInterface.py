from abc import ABC, abstractmethod
import os

import numpy as np
import tensorflow as tf

import logging

from perceptilabs.createDataObject import createDataObject


log = logging.getLogger(__name__)

class LW_interface_base(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError

    def _try_fetch(self, dict, variable):
        try:
            return dict[variable]
        except:
            return ""


class getDataMeta(LW_interface_base):
    def __init__(self, id_, lw_core, data_container):
        self._id = id_
        self.lw_core = lw_core
        self.data_container = data_container

    def run(self):
        # lw_core, _, data_container = self.lwObj.create_lw_core()
        self.lw_core.run()
        content = {
            "Action_space": self._try_fetch(self.data_container[self._id], "_action_space"),
            "Dataset_size": self._try_fetch(self.data_container[self._id], "_data_size"),
            "Columns": self._try_fetch(self.data_container[self._id], "cols")
        }
        return content

class getGraphOrder(LW_interface_base):
    def __init__(self, jsonNetwork):
        self.jsonNetwork = jsonNetwork

    def run(self):
        from perceptilabs.graph import Graph
        graph = Graph(self.jsonNetwork)
        graph_dict = graph.graphs
        return list(graph_dict.keys())

class getPartitionSummary(LW_interface_base):
    def __init__(self, id_, lw_core, data_container):
        self._id = id_
        self.lw_core = lw_core
        self.data_container = data_container

    def run(self):
        self.lw_core.run()
        content = self._try_fetch(self.data_container[self._id], "_action_space")
        return content

    
class getCodeV2(LW_interface_base):
    def __init__(self, id_, network):
        self._id = id_
        self._network = network

    def run(self):
        from perceptilabs.core_new.graph import Graph
        from perceptilabs.core_new.graph.builder import GraphBuilder
        from perceptilabs.core_new.layers.script import ScriptFactory
        from perceptilabs.core_new.graph.utils import sanitize_layer_name

        graph_builder = GraphBuilder()        
        graph = graph_builder.build_from_spec({'Layers': self._network})        
        layer_name = self._network[self._id]['Name']
        node = graph.get_node_by_id(sanitize_layer_name(layer_name)) # NOTE: graph currently uses a sanitized layer name for Id.

        script_factory = ScriptFactory()        
        code = script_factory.render_layer_code(node)

        return {'Output': code}        

        
class getCodeV1(LW_interface_base):
    def __init__(self, id_, network):
        self._id = id_
        self._network = network

    def run(self):
        if self._network[self._id]["Type"] == "TrainReinforce":
            from perceptilabs.graph import Graph
            graph = Graph(self._network)
            graph_dict = graph.graphs
            layerInfo = graph_dict[self._id]
        else:
            layerInfo = {"Info": {
                                  "Type": self._network[self._id]["Type"], "Id": self._id,
                                  "Properties": self._network[self._id]['Properties'],
                                  "backward_connections": self._network[self._id]["backward_connections"],
                                  "forward_connections": self._network[self._id]["forward_connections"]
                                  },
                                  "Con": self._network[self._id]["backward_connections"],
                                  
                                  }

        from perceptilabs.codehq import CodeHqNew as CodeHq

        content = {"Output": CodeHq.get_code_generator(self._id,layerInfo).get_code()}
        return content

class getNetworkInputDim(LW_interface_base):
    def __init__(self, network, lw_core, extras_reader):
        self._network = network
        self.lw_core = lw_core
        self.extras_reader = extras_reader

    def run(self):
        self.lw_core.run()

        content={}

        extras_dict=self.extras_reader.to_dict()
        for id_, value in self._network.items():
            content[id_]={}

            con=[con_id for con_id, con_name in value['backward_connections']]

            if len(con)==1 and con[0] in extras_dict:
                content[id_].update({"inShape":str(extras_dict[con[0]]["outShape"])})
            else:
                tmp=[]
                for i in con:
                    if i in extras_dict:
                        tmp.append(extras_dict[i]["outShape"])
                tmp=np.squeeze(tmp).tolist()

                content[id_].update({"inShape":str(tmp).replace("'","")})

            if id_ in self.lw_core.error_handler:
                log.info("ErrorMessage: " + str(self.lw_core.error_handler[id_]))

                content[id_]['Error'] = {
                    'Message': self.lw_core.error_handler[id_].error_message,
                    'Row': self.lw_core.error_handler[id_].error_line
                }
            else:
                content[id_]['Error'] = None

        return content

class getNetworkOutputDim(LW_interface_base):
    def __init__(self, lw_core, extras_reader):
        self.lw_core = lw_core
        self.extras_reader = extras_reader

    def run(self):                      
        self.lw_core.run()
        
        extrasDict=self.extras_reader.to_dict()

        content={}

        for Id, value in extrasDict.items():
            content[Id]={}
            content[Id].update({"Dim": str(value["outShape"]).replace("[","").replace("]","").replace(", ","x")})

            if Id in self.lw_core.error_handler:
                log.info("ErrorMessage: " + str(self.lw_core.error_handler[Id]))

                content[Id]['Error'] = {
                    'Message': self.lw_core.error_handler[Id].error_message,
                    'Row': self.lw_core.error_handler[Id].error_line
                }
            else:
                content[Id]['Error'] = None  

        return content           

class getPreviewSample(LW_interface_base):
    def __init__(self, id_, lw_core, extras_reader, data_container, variable=None):
        self._id = id_
        self.lw_core = lw_core
        self.extras_reader = extras_reader
        self.data_container = data_container
        self._variable = variable

    def _is_jsonable(self, x):
        import json

        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def _reduceTo2d(self, data):
            data_shape=np.shape(np.squeeze(data))
            if len(data_shape)<=2 or (len(data_shape)==3 and (data_shape[-1]==3 or data_shape[-1]==1)):
                return data
            else:
                return self._reduceTo2d(data[...,-1])
    
    def run(self):                                
        self.lw_core.run()
        
        sample=""
        if self._variable:
            dataContainerDict=self.data_container.to_dict()
            if self._id in dataContainerDict:
                sample = dataContainerDict[self._id][self._variable]
        else:
            extrasDict=self.extras_reader.to_dict()
            if self._id in extrasDict:
                sample = extrasDict[self._id]["Sample"]


        if isinstance(sample,tf.Variable):
            sample=sample.numpy()

        if len(np.shape(sample))>1:
            sample=np.squeeze(sample)

        
        dataObject=createDataObject([self._reduceTo2d(np.asarray(sample))])
        
        if self._is_jsonable(dataObject):
            content = dataObject
        else:
            content = createDataObject([""])

        return content

class getPreviewVariableList(LW_interface_base):
    def __init__(self, id_, network, lw_core, extras_reader):
        self._id = id_
        self._network = network
        self.lw_core = lw_core
        self.extras_reader = extras_reader

    def run(self):                                            
        self.lw_core.run()
        
        extrasDict=self.extras_reader.to_dict()
        if self._id in extrasDict:
            content = {
                "VariableList": extrasDict[self._id]["Variables"],
                "VariableName": extrasDict[self._id]["Default_var"],
            }

            if self._id in self.lw_core.error_handler:
                log.info("ErrorMessage: " + str(self.lw_core.error_handler[self._id]))
                
                content['Error'] = {
                    'Message': self.lw_core.error_handler[self._id].error_message,
                    'Row': self.lw_core.error_handler[self._id].error_line
                }
        else:
            content = ""

        return content

class Parse(LW_interface_base):
    def __init__(self, pb, checkpointDict, checkpoint=None, make_trainable=True, end_points="", containerize=False):
        self._pb = pb
        self._checkpointDict = checkpointDict
        self._checkpoint = checkpoint
        self._make_trainable = make_trainable
        self._end_points = end_points
        self._containerize = containerize

    def _getParsingFiles(self, pb, checkpoint):
        if checkpoint=="" and "." not in pb.split("/")[-1]:
            #Then its a folder
            raise Exception("Tried to parse a folder")

        if ".pb" in pb and not checkpoint:
            return [pb,None]
        elif ".pb" not in pb:
            raise Exception("Only frozen .pb files can be parsed by themselves")
        else:
            if "ckpt" not in checkpoint:
                raise Exception("Wrong file type")
            checkpoint = checkpoint.split("ckpt")[0]         
            return [pb, checkpoint]

    def run(self):
        try:
            correct_file_list=self._getParsingFiles(self._pb, self._checkpoint)
        except Exception as e:
            return e

        filteredValueDict=None
        try:
            from parse_pb import parse
            content, filteredValueDict=parse(self._make_trainable, self._end_points, *correct_file_list)
        except Exception as e:
            raise Exception("Could not parse the file.\n"+str(e))
        
        if type(filteredValueDict) is dict:
            self._checkpointDict[correct_file_list[-1]]=filteredValueDict
        # else:
            # warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
        
        return content
