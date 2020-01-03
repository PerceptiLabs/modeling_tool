from abc import ABC, abstractmethod

import numpy as np
import tensorflow as tf

import logging
log = logging.getLogger(__name__)

class LW_interface_base(ABC):
    @abstractmethod
    def exec(self):
        raise NotImplementedError


class getDataMeta(LW_interface_base):
    def __init__(self, id_, lwObj):
        self._id = id_
        self.lwObj = lwObj
        # self._network = network
        # self._lw_func = lw_func

    def _try_fetch(self, dict, variable):
        try:
            return dict[variable]
        except:
            return ""

    def exec(self):
        lw_core, _, data_container = self.lwObj.create_lw_core()
        lw_core.run()
        content = {
            "Action_space": self._try_fetch(data_container[self._id], "_action_space"),
            "Dataset_size": self._try_fetch(data_container[self._id], "_data_size"),
            "Columns": self._try_fetch(data_container[self._id], "cols")
        }
        return content


class getPartitionSummary(LW_interface_base):
    def __init__(self, id_, network, lw_func):
        self._id = id_
        self._network = network
        self._lw_func = lw_func

    def _try_fetch(self, dict, variable):
        try:
            return dict[variable]
        except:
            return ""

    def exec(self):
        lw_core, _, data_container = self._lw_func(self._network)
        lw_core.run()
        content = self._try_fetch(data_container[self._id], "_action_space")
        return content


class getCode(LW_interface_base):
    def __init__(self, id_, network):
        self._id = id_
        self._network = network

    def exec(self):
        if self._network[self._id]["Type"] == "TrainReinforce":
            from graph import Graph
            graph = Graph(self._network)
            graph_dict = graph.graphs
            layerInfo = graph_dict[self._id]
        else:
            layerInfo = {"Info": {
                                  "Type": self._network[self._id]["Type"], "Id": self._id,
                                  "Properties": self._network[self._id]['Properties']}, 
                                  "Con": self._network[self._id]["backward_connections"]
                                  }

        from codehq import CodeHqNew as CodeHq

        content = {"Output": CodeHq.get_code_generator(self._id,layerInfo).get_code()}
        return content

class getNetworkInputDim(LW_interface_base):
    def __init__(self, network, lw_func):
        self._network = network
        self._lw_func = lw_func

    def exec(self):
        lw_core, extras_reader, _ = self._lw_func(self._network)
        lw_core.run()

        content={}

        extras_dict=extras_reader.to_dict()
        for id_, value in self._network.items():
            content[id_]={}

            con=value['backward_connections']

            if len(con)==1 and con[0] in extras_dict:
                content[id_].update({"inShape":str(extras_dict[con[0]]["outShape"])})
            else:
                tmp=[]
                for i in con:
                    if i in extras_dict:
                        tmp.append(extras_dict[i]["outShape"])
                tmp=np.squeeze(tmp).tolist()

                content[id_].update({"inShape":str(tmp).replace("'","")})

            if id_ in lw_core.error_handler:
                log.info("ErrorMessage: " + str(lw_core.error_handler[id_]))

                content[id_]['Error'] = {
                    'Message': lw_core.error_handler[id_].error_message,
                    'Row': lw_core.error_handler[id_].error_line
                }
            else:
                content[id_]['Error'] = None

        return content

class getNetworkOutputDim(LW_interface_base):
    def __init__(self, network, lw_func):
        self._network = network
        self._lw_func = lw_func

    def exec(self):
        lw_core, extras_reader, _ = self._lw_func(self._network)                        
        lw_core.run()
        
        extrasDict=extras_reader.to_dict()

        content={}

        for Id, value in extrasDict.items():
            content[Id]={}
            content[Id].update({"Dim": str(value["outShape"]).replace("[","").replace("]","").replace(", ","x")})

            if Id in lw_core.error_handler:
                log.info("ErrorMessage: " + str(lw_core.error_handler[Id]))

                content[Id]['Error'] = {
                    'Message': lw_core.error_handler[Id].error_message,
                    'Row': lw_core.error_handler[Id].error_line
                }
            else:
                content[Id]['Error'] = None  

        return content           

class getPreviewSample(LW_interface_base):
    def __init__(self, id_, network, lw_func, variable=None):
        self._id = id_
        self._network = network
        self._lw_func = lw_func
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
    
    def exec(self):
        lw_core, extras_reader, data_container = self._lw_func(self._network)                                    
        lw_core.run()
        
        sample=""
        if self._variable:
            dataContainerDict=data_container.to_dict()
            if self._id in dataContainerDict:
                sample = dataContainerDict[self._id][self._variable]
        else:
            extrasDict=extras_reader.to_dict()
            if self._id in extrasDict:
                sample = extrasDict[self._id]["Sample"]


        if isinstance(sample,tf.Variable):
            sample=sample.numpy()

        if len(np.shape(sample))>1:
            sample=np.squeeze(sample)

        
        from createDataObject import createDataObject
        dataObject=createDataObject([self._reduceTo2d(np.asarray(sample))])
        
        if self._is_jsonable(dataObject):
            content = dataObject
        else:
            content = createDataObject([""])

        return content

class getPreviewVariableList(LW_interface_base):
    def __init__(self, id_, network, lw_func):
        self._id = id_
        self._network = network
        self._lw_func = lw_func

    def exec(self):
        lw_core, extras_reader, _ = self._lw_func(self._network)                                                
        lw_core.run()
        
        extrasDict=extras_reader.to_dict()
        if self._id in extrasDict:
            content = {
                "VariableList": extrasDict[self._id]["Variables"],
                "VariableName": extrasDict[self._id]["Default_var"],
            }

            if self._id in lw_core.error_handler:
                log.info("ErrorMessage: " + str(lw_core.error_handler[self._id]))
                
                content['Error'] = {
                    'Message': lw_core.error_handler[self._id].error_message,
                    'Row': lw_core.error_handler[self._id].error_line
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
        if ".pb" in pb:
            return [pb, None]
        elif ".pb" not in pb and not checkpoint:
            raise Exception("Only frozen .pb files can be parsed by themselves")

        if checkpoint:
            if "ckpt" not in checkpoint:
                raise Exception("Wrong file type")
            checkpoint = checkpoint.split("ckpt")[0]
            return [pb, checkpoint]

    def exec(self):
        try:
            correct_file_list=self._getParsingFiles(self._pb, self._checkpoint)
        except Exception as e:
            return e

        filteredValueDict=None
        try:
            from parse_pb import parse
            content, filteredValueDict=parse(self._make_trainable, self._end_points, *correct_file_list)
        except Exception as e:
            raise "Could not parse the file.\n"+str(e)
        
        if type(filteredValueDict) is dict:
            self._checkpointDict[correct_file_list[-1]]=filteredValueDict
        # else:
            # warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
        
        return content