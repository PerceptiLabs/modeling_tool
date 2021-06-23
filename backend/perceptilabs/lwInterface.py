from abc import ABC, abstractmethod
import os
import logging
import numpy as np
import tensorflow as tf
import platform
import shutil


from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.spec import GraphSpec
from perceptilabs.createDataObject import createDataObject, subsample_data
import perceptilabs.logconf
import perceptilabs.utils as utils


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
        
    def _reduceTo2d(self, data):
        data_shape=np.shape(np.squeeze(data))
        if len(data_shape)<=2 or (len(data_shape)==3 and (data_shape[-1]==3 or data_shape[-1]==1)):
            return data
        else:
            return self._reduceTo2d(data[...,-1])
        

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
        graph_spec = GraphSpec.from_dict(self.jsonNetwork)
        ordered_ids = graph_spec.get_ordered_ids()
        return list(ordered_ids)

    
class getNotebookRunscript(LW_interface_base):
    def __init__(self, jsonNetwork):
        self.jsonNetwork = jsonNetwork

    def run(self):
        graph_spec = GraphSpec.from_dict(self.jsonNetwork)
        script_factory = ScriptFactory()
        return script_factory.get_runscript(graph_spec)

    
class getNotebookImports(LW_interface_base):
    def __init__(self, jsonNetwork):
        self.jsonNetwork = jsonNetwork

    def run(self):
        graph_spec = GraphSpec.from_dict(self.jsonNetwork)
        script_factory = ScriptFactory()
        return script_factory.get_imports(graph_spec)


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
                logger.warning("ErrorMessage: " + str(self.lw_core.error_handler[self._id]))
                
                content[self._id]['Error'] = {
                    'Message': self.lw_core.error_handler[self._id].message,
                    'Row': str(self.lw_core.error_handler[self._id].line_number)
                }
            else:
                content[self._id]['Error'] = None
                
        return content

    
class GetNetworkInputDim(LW_interface_base):
    """ Used in some layers to validate values or to populate default values. 
    E.g., in reshape and rescale 
    """
    
    def __init__(self, lw_core, graph_spec):
        self._lw_core = lw_core
        self._graph_spec = graph_spec

    def run(self):
        lw_results = self._lw_core.run(self._graph_spec)

        content = {
            layer_spec.id_: self._get_layer_content(layer_spec, lw_results)
            for layer_spec in self._graph_spec.layers
        }
        return content

    def _get_layer_content(self, layer_spec, lw_results):
        # Set the preview shape 
        shape_str = '[]' # Default
        if len(layer_spec.backward_connections) > 0:
            conn = layer_spec.backward_connections[0]
            input_results = lw_results.get(conn.src_id).sample

            if input_results is not None:
                sample = input_results.get(conn.src_var)
                shape = np.squeeze(sample.shape).tolist() if sample is not None else []
                shape_str = str(shape)

        content = {'inShape': shape_str}

        # Set the errors
        layer_results = lw_results[layer_spec.id_]

        if layer_spec.should_show_errors and layer_results.has_errors:
            error_type, error_info = list(layer_results.errors)[-1] # Get the last error
            content['Error'] = {'Message': error_info.message, 'Row': error_info.line_number}
        else:
            content['Error'] = None

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
                logger.warning("ErrorMessage: " + str(self.lw_core.error_handler[Id]))

                content[Id]['Error'] = {
                    'Message': self.lw_core.error_handler[Id].message,
                    'Row': str(self.lw_core.error_handler[Id].line_number)
                }
            else:
                content[Id]['Error'] = None  
        return content
    
        
class getPreviewSample(LW_interface_base):
    def __init__(self, layer_id, lw_core, graph_spec, variable):
        self._layer_id = layer_id
        self._lw_core = lw_core
        self._graph_spec = graph_spec
        self._variable = variable

    def _is_jsonable(self, x):
        import json

        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False
    
    def run(self):
        results = self._lw_core.run(self._graph_spec)

        if self._variable in ['sample', '(sample)']:
            return 'output'

        try:
            sample = results[self._layer_id].sample[self._variable]
        except:
            print(results[self._layer_id].sample.keys())            
            raise
        
        dataObject=createDataObject([self._reduceTo2d(np.asarray(sample))])
        
        if self._is_jsonable(dataObject):
            content = dataObject
        else:
            content = createDataObject([""])

        return content

    
class getPreviewBatchSample(LW_interface_base):
    def __init__(self, lw_core, graph_spec, json_network):
        self._lw_core = lw_core
        self._graph_spec = graph_spec
        self._json_network = json_network

    def _is_jsonable(self, x):
        import json
        
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False
        
    def run(self):                                
        results = self._lw_core.run(self._graph_spec)
        returnJson = {}
        trained_layers = {}
        for id_, data in results.items():
            trained_layers[id_] = data.trained               
            if 'getPreview' in self._json_network[id_] and self._json_network[id_]['getPreview']:
                if 'previewVariable' in self._json_network[id_]:
                    try:
                        sample = data.sample[self._json_network[id_]['previewVariable']]
                        dataObject = createDataObject([self._reduceTo2d(np.asarray(sample).squeeze())])
                        if self._is_jsonable(dataObject):
                            returnJson[id_] = dataObject
                        else:
                            returnJson[id_] = None
                    except:
                        logger.warning(f"A visualization of output variable '{self._json_network[id_]['previewVariable']}' could not be created for component '{self._json_network[id_]['Name']}'")
                        returnJson[id_] = None             
                else:
                    returnJson[id_] = None
            else:
                continue

        self._maybe_log_obj_sizes(returnJson)
        return returnJson, trained_layers

    def _maybe_log_obj_sizes(self, returnJson):
        if not logger.isEnabledFor(logging.DEBUG):
            return
        
        for id_, data_obj in returnJson.items():
            for s in data_obj['series']:
                try:
                    logger.info(
                        f"preview sample {id_}: length {len(s['data'])}, "
                        f"height {s['height']}, width {s['width']}"
                    )
                except:
                    pass
            

class getPreviewVariableList(LW_interface_base):
    def __init__(self, layer_id, lw_core, graph_spec):
        self._layer_id = layer_id
        self._lw_core = lw_core
        self._graph_spec = graph_spec

    def run(self):

        results = self._lw_core.run(self._graph_spec)
        layer_info = results[self._layer_id]
        
        sample = layer_info.sample
        error = layer_info.strategy_error or layer_info.instantiation_error or layer_info.code_error


        content = {
            "VariableList": list(sample.keys()),
            "VariableName": "output"
        }

        if error is not None:
            content['Error'] = {
                'Message': error.message,
                'Row': str(error.line_number)
            }
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


class ScanCheckpoint(LW_interface_base):
    def __init__(self, path):
        self._path = path

    def run(self):
        response = False
        if 'checkpoint' in os.listdir(self._path):
            for filename in os.listdir(os.path.join(self._path,'checkpoint')):
                if filename == 'checkpoint':
                    response = True
                    break
        return response


class CopyJsonModel(LW_interface_base):
    def __init__(self, folder_path):
        self._folder_path = folder_path
    def run(self):
        import time
        file_path = os.path.join(self._folder_path, 'model.json')
        copy_path = os.path.join(self._folder_path, 'checkpoint','checkpoint_model.json')
        if not os.path.isdir(os.path.join(self._folder_path,'checkpoint')):
            os.mkdir(os.path.join(self._folder_path,'checkpoint'))
            time.sleep(.0000000000000001) #Force your computer to do a clock cycle to avoid Windows issues
        shutil.copy2(file_path, copy_path)
        time.sleep(.0000000000000001) #Force your computer to do a clock cycle to avoid Windows issues        


class UploadKernelLogs(LW_interface_base):
    """ Uploads the Kernel logs to Azure and associates them to a GitHub issue"""
    def __init__(self, content, session_id):
        """ 
        Args:
            content: the json request coming from the frontend
            session_id: the ID of the current kernel session
        """
        
        self._issue_title = content['issueTitle']
        self._issue_body = content['issueBody']
        self._github_issue_number = content['gitHubIssueNumber']
        self._github_issue_url = content['gitHubIssueUrl']
        self._session_id = session_id

    def run(self):
        import time
        """ Uploads logs to Azure """
        # NOTE: this should be logged _before_ the logs are uploaded
        # so that the information is also embedded in the log
        logger.info(
            f"User reported an issue.\n"
            f"Title: {self._issue_title}\n"
            f"Issue number: {self._github_issue_number}.\n"
            f"Issue url: {self._github_issue_url}.\n"
            f"Body: \n{self._issue_body}"
        )

        zip_name = utils.format_logs_zipfile_name(self._session_id, self._github_issue_number)
        try:
            perceptilabs.logconf.upload_logs(zip_name)
        except:
            logger.exception("Failed uploading logs for!")
            return False
        else:
            return True
            
