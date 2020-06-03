from abc import ABC, abstractmethod
import os
import logging
import numpy as np
import tensorflow as tf

from perceptilabs.logconf import APPLICATION_LOGGER
import platform

from perceptilabs.createDataObject import createDataObject
from perceptilabs.core_new.core import Core

logger = logging.getLogger(APPLICATION_LOGGER)


class LW_interface_base(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError

    def _try_fetch(self, dict, variable):
        try:
            return dict[variable]
        except:
            return ""


class saveJsonModel(LW_interface_base):
    def __init__(self, save_path, json_model):
        self._save_path = save_path
        self._json_model = json_model

    def run(self):
        import json
        full_path = os.path.expanduser(self._save_path)

        if not os.path.isdir(full_path):
            os.mkdir(full_path)
        
        file_path = os.path.join(full_path, 'model.json')
        with open(file_path, 'w') as outfile:
            json.dump(json.loads(self._json_model), outfile)

class getFolderContent(LW_interface_base):
    def __init__(self, current_path):
        self._current_path = current_path

    def run(self):
        if not self._current_path:
            # self._current_path = os.path.abspath('')
            #TODO Make it a seperate request to get the path to tutorial_data
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'tutorial_data')
            if os.path.exists(path):
                self._current_path = path    
            else:
                self._current_path = os.path.abspath('')

        drives = []
        if self._current_path == '.' and platform.system() == 'Windows':            
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]

        elif not os.path.isdir(self._current_path):
            return {
                "current_path" : '',
                "dirs" : '',
                "files" :  '',
                "platform": platform.system(),
            }
        
        if not drives:
            return {
                "current_path" : self._current_path.replace('\\','/'),
                "dirs" : [x for x in os.listdir(self._current_path) if os.path.isdir(os.path.join(self._current_path,x))],
                "files" :  [x for x in os.listdir(self._current_path) if os.path.isfile(os.path.join(self._current_path,x))],
                "platform": platform.system(),
            }
        else:
            return {
                "current_path" : self._current_path.replace('\\','/'),
                "dirs" : drives,
                "files" :  [],
                "platform": platform.system(),
            }
class getJsonModel(LW_interface_base):
    def __init__(self, json_path):
        self._json_path = os.path.expanduser(json_path)
    
    def run(self):
        if not os.path.exists(self._json_path):
            return ""
        
        import json
        with open(self._json_path, 'r') as f:
            json_model = json.load(f)
        return json_model

class createFolder(LW_interface_base):
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def run(self):
        try:
            import platform

            if platform.system() == 'Windows':
                resolved_path = self.resolveWindowsPath(self.folder_path)
                expanded_path = os.path.normpath(resolved_path)
                
            else:
                expanded_path = os.path.expanduser(self.folder_path)

            os.makedirs(expanded_path, exist_ok=True)
            return expanded_path 

        except:
            return ''
    
    def resolveWindowsPath(self, inputPath):
        if '~/Documents' in inputPath:
            # get My Documents regardless of localization
            import ctypes.wintypes
            
            buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            _ = ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 5, buf)

            return inputPath.replace('~/Documents', buf.value)
        
        elif '~/' in inputPath:
            return os.path.expanduser(inputPath)

        else:
            return inputPath

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

    
class getDataMetaV2(LW_interface_base):
    def __init__(self, id_, lw_core, extras_reader):
        self._id = id_
        self.lw_core = lw_core
        self.extras_reader = extras_reader

    def run(self):
        # lw_core, _, data_container = self.lwObj.create_lw_core()
        self.lw_core.run()
        extras_dict = self.extras_reader.to_dict()
        cols = extras_dict[self._id].get("cols", '')
        action_space = extras_dict[self._id].get("action_space", '')
        content = {
            "Action_space": action_space,
            "Dataset_size": "",
            "Columns": cols
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

class getNotebookRunscript(LW_interface_base):
    def __init__(self, jsonNetwork):
        self.jsonNetwork = jsonNetwork

    def run(self):
        from perceptilabs.core_new.layers.script import ScriptFactory
        from perceptilabs.core_new.graph.builder import GraphBuilder
        
        script_factory = ScriptFactory()
        graph_builder = GraphBuilder()
        graph = graph_builder.build_from_spec(self.jsonNetwork)

        return script_factory.get_runscript(graph)

class getNotebookImports(LW_interface_base):
    def __init__(self, jsonNetwork):
        self.jsonNetwork = jsonNetwork

    def run(self):
        from perceptilabs.core_new.layers.script import ScriptFactory
        from perceptilabs.core_new.graph.builder import GraphBuilder
        
        script_factory = ScriptFactory()
        graph_builder = GraphBuilder()
        graph = graph_builder.build_from_spec(self.jsonNetwork)

        return script_factory.get_imports(graph)


class getPartitionSummary(LW_interface_base):
    def __init__(self, id_, lw_core, data_container):
        self._id = id_
        self.lw_core = lw_core
        self.data_container = data_container

    def run(self):
        self.lw_core.run()
        content = self._try_fetch(self.data_container[self._id], "_action_space")

        if isinstance(content, dict):
            if self._id in self.lw_core.error_handler:
                logger.info("ErrorMessage: " + str(self.lw_core.error_handler[self._id]))
                
                content[self._id]['Error'] = {
                    'Message': self.lw_core.error_handler[self._id].message,
                    'Row': str(self.lw_core.error_handler[self._id].line_number)
                }
            else:
                content[self._id]['Error'] = None
                
        return content

    
class getCodeV2(LW_interface_base):
    def __init__(self, id_, network):
        self._id = id_
        self._network = network



    def run(self):
        from perceptilabs.core_new.graph import Node
        from perceptilabs.core_new.layers.script import ScriptFactory
        from perceptilabs.core_new.graph.utils import sanitize_layer_name

        layer_spec = self._network[self._id].copy()
        layer_type = layer_spec['Type']

        #TODO: Remove this if-case when frontend is sending back correct file path on Windows
        if layer_type == "DataData" and layer_spec['Properties'] is not None:
            sources = layer_spec['Properties']['accessProperties']['Sources']
            new_sources = []
            for source in sources:
                tmp = source
                if tmp["path"]:
                    tmp["path"] = tmp["path"].replace("\\","/")
                new_sources.append(tmp)
            layer_spec['Properties']['accessProperties']['Sources'] = new_sources

        layer_id = sanitize_layer_name(layer_spec['Name'])
        layer_instance = None
        node = Node(layer_id, layer_type, layer_instance, layer_spec)
        
        script_factory = ScriptFactory()        
        code = script_factory.render_layer_code(node.layer_id, node.layer_type, node.layer_spec, node.custom_code)
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
                logger.info("ErrorMessage: " + str(self.lw_core.error_handler[id_]))

                content[id_]['Error'] = {
                    'Message': self.lw_core.error_handler[id_].message,
                    'Row': str(self.lw_core.error_handler[id_].line_number)
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
                logger.info("ErrorMessage: " + str(self.lw_core.error_handler[Id]))

                content[Id]['Error'] = {
                    'Message': self.lw_core.error_handler[Id].message,
                    'Row': str(self.lw_core.error_handler[Id].line_number)
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
                logger.info("ErrorMessage: " + str(self.lw_core.error_handler[self._id]))
                
                content['Error'] = {
                    'Message': self.lw_core.error_handler[self._id].message,
                    'Row': str(self.lw_core.error_handler[self._id].line_number)
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
