import asyncio
import websockets
import ssl
import json
import struct
import io
import time
import traceback

from coreLogic import coreLogic
from propegateNetwork import lwNetwork
from parse_pb import parse
import time
import numpy as np

from dataKeeper import dataKeeper as lw_data
from extractVariables import *
from createDataObject import createDataObject

from core_new.core import *
from core_new.history import SessionHistory
from core_new.errors import LightweightErrorHandler
from core_new.extras import LayerExtrasReader
from core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
from graph import Graph
from codehq import CodeHqNew as CodeHq
from modules import ModuleProvider
from core_new.cache import get_cache
from core_new.networkCache import NetworkCache

import pprint
import logging

class Message:
    def __init__(self, cores, dataDict, checkpointDict, lwDict):
        self.cores=cores
        self.dataDict=dataDict
        self.checkpointDict=checkpointDict
        self.lwDict=lwDict

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def process_protoheader(self, request):
        hdrlen = 2
        if len(request) >= hdrlen:
            jsonheader_len = struct.unpack(
                ">H", request[:hdrlen]
            )[0]
            request = request[hdrlen:]
        return (request,jsonheader_len)

    def process_jsonheader(self, request,jsonheader_len):
        hdrlen = jsonheader_len
        if len(request) >= hdrlen:
            jsonheader = self._json_decode(
                request[:hdrlen], "utf-8"
            )
            request = request[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in jsonheader:
                    raise ValueError("Missing required header " + reqhdr)
        return (request,jsonheader)

    def process_request(self, request,jsonheader):
        content_len = jsonheader["content-length"]
        if not len(request) >= content_len:
            return
        data = request[:content_len]
        request = request[content_len:]
        if jsonheader["content-type"] == "text/json":
            encoding = jsonheader["content-encoding"]
            request = self._json_decode(data, encoding)
            print("received request", repr(request))
        else:
            # Binary or unknown content-type
            request = data
            print("received" + str(jsonheader["content-type"]) + " request from")

        return request
    
    def _is_jsonable(self, x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def add_to_checkpointDict(self, content):
        if content["checkpoint"][-1] not in self.checkpointDict:
            from extractVariables import extractCheckpointInfo
            ckptObj=extractCheckpointInfo(content["endPoints"], *content["checkpoint"])
            self.checkpointDict[content["checkpoint"][-1]]=ckptObj.getVariablesAndConstants()
            ckptObj.close()

    def _create_lw_core(self, jsonNetwork, reciever):
        if reciever not in self.lwDict:
            self.lwDict[reciever]=NetworkCache()
        else:
            deleteList=[]
            for layer_id in self.lwDict[reciever].get_layers():
                if layer_id not in jsonNetwork:
                    deleteList.append(layer_id)
            log.info("Deleting these layers: " + str(deleteList))
            for layer_id in deleteList:
                self.lwDict[reciever].remove_layer(layer_id)

        graph = Graph(jsonNetwork)
        
        graph_dict = graph.graphs

        for value in graph_dict.values():
            if "checkpoint" in value["Info"] and value["Info"]["checkpoint"]:
                self.add_to_checkpointDict(value["Info"])

        data_container = DataContainer()


            
        extras_reader = LayerExtrasReader()

        from codehq import CodeHqNew as CodeHq

        module_provider = ModuleProvider()
        module_provider.load('tensorflow', as_name='tf')
        module_provider.load('numpy', as_name='np')
        module_provider.load('pandas', as_name='pd')             
        module_provider.load('gym')
        module_provider.load('json')  
        module_provider.load('os')   
        module_provider.load('skimage')         
        module_provider.load('dask.array', as_name='da')
        module_provider.load('dask.dataframe', as_name='dd')                  
        
        for hook_target, hook_func in LW_ACTIVE_HOOKS.items():
            module_provider.install_hook(hook_target, hook_func)

        error_handler = LightweightErrorHandler()
        
        global session_history_lw
        cache = get_cache()
        session_history_lw = SessionHistory(cache) # TODO: don't use global!!!!        
        lw_core = LightweightCore(CodeHq, graph_dict,
                                  data_container, session_history_lw,
                                  module_provider, error_handler,
                                  extras_reader, checkpointValues=self.checkpointDict.copy(),
                                  network_cache=self.lwDict[reciever])
        
        return lw_core, extras_reader, data_container

    def getParsingFiles(self,fileList):
        if len(fileList)==1 and "." not in fileList[0].split("/")[-1]:
            #Then its a folder
            return ""
        elif len(fileList)==1:
            if ".pb" in fileList[0]:
                return [fileList[0],None]
            else:
                raise Exception("Only frozen .pb files can be parsed by themselves")
        else:
            graph_def_path=""
            checkpoint=""
            for _file in fileList:
                if ".ckpt" in _file:
                    path, fileName=os.path.split(_file)
                    if "ckpt" in fileName.split(".")[-1]:
                        checkpoint=_file
                    else:
                        newFileName=".".join(fileName.split(".")[0:-1])
                        checkpoint=os.path.abspath(os.path.join(path, newFileName))
                    
                elif any([pb in _file for pb in [".pb", ".pbtxt"]]):
                    graph_def_path=_file
                else:
                    raise Exception("File type not recognised")
            if graph_def_path and checkpoint:
                return [graph_def_path, checkpoint]
            else:
                return ""

    async def interface(self, websocket, path):
        request = await websocket.recv()
        print("request: ", request)
        request, jsonheader_len=self.process_protoheader(request)
        request, jsonheader=self.process_jsonheader(request,jsonheader_len)
        message=self.process_request(request,jsonheader)

        request=self._json_decode(request,"utf-8")
        
        reciever = request.get("reciever")
        action = request.get("action")


        if not reciever in self.dataDict:
            self.dataDict[reciever]=dict()

        if reciever not in self.cores:
            core=coreLogic(reciever)
            self.cores[reciever]=core
        else:
            core=self.cores[reciever]

        warnings=core.warningQueue
        warningList=[]

        errors=core.errorQueue
        errorList=[]

        content=""

        #####################################B4End###################################
        if action == "getDataMeta":
            value=request.get("value")
            Id=value["Id"]
            jsonNetwork=value["Network"]
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, _, data_container = self._create_lw_core(jsonNetwork, reciever)
            lw_core.run()


            def try_fetch(dict,variable):
                try:
                    return dict[variable]
                except:
                    return ""

            content={
                "Action_space": try_fetch(data_container[Id],"_action_space"),
                "Dataset_size": try_fetch(data_container[Id], "_data_size"),
                "Columns": try_fetch(data_container[Id], "cols")
            }


        elif action == "getPartitionSummary":
            value=request.get("value")
            Id=value["Id"]
            jsonNetwork=value["Network"]
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings

            lw_core, _, data_container = self._create_lw_core(jsonNetwork, reciever)
            lw_core.run()

            def try_fetch(dict,variable):
                try:
                    return dict[variable]
                except:
                    return ""

            content=try_fetch(data_container[Id],"_partition_summary")


        elif action == "deleteData":
            value=request.get("value")
            if value["Id"] in self.dataDict[reciever]:
                del self.dataDict[reciever][value["Id"]]
                content={"content": "Deleted data on workspace " + str(reciever) + " with Id: " +str(value["Id"])+"."}
            else:
                content={"content": "No such Id had saved data in that workspace"}

        elif action == "removeReciever":
            for value in self.dataDict[reciever].values():
                del value
            del self.dataDict[reciever]
            content={"content": "All data on workspace " + str(reciever) + " has been deleted"}

        elif action == "getCode":
            value=request.get("value")
            jsonNetwork=value['Network']
            Id = value['Id']
            if "layerSettings" in value:
                layerSettings = value["layerSettings"]
                jsonNetwork[Id]["Properties"]=layerSettings
            

            if jsonNetwork[Id]["Type"] == "TrainReinforce":
                graph=Graph(jsonNetwork)
                graph_dict = graph.graphs
                layerInfo=graph_dict[Id]
            else:
                layerInfo={"Info":{"Type":jsonNetwork[Id]["Type"], "Id": Id, "Properties": jsonNetwork[Id]['Properties']}, "Con":jsonNetwork[Id]["backward_connections"]}

            from codehq import CodeHqNew as CodeHq
            
            content = {"Output": CodeHq.get_code_generator(Id,layerInfo).get_code()}

        elif action == "getNetworkInputDim":
            jsonNetwork=request.get("value")

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)            
            lw_core.run()
            
            content={}

            extras_dict=extras_reader.to_dict()
            for Id, value in jsonNetwork.items():
                extras_value={}
                content[Id]={}

                if Id in extras_dict:
                    extras_value=extras_dict[Id]

                con=value['backward_connections']

                if len(con)==1 and con[0] in extras_dict:
                    content[Id].update({"inShape":str(extras_dict[con[0]]["outShape"])})
                else:
                    tmp=[]
                    for i in con:
                        if i in extras_dict:
                            tmp.append(extras_dict[i]["outShape"])
                    tmp=np.squeeze(tmp).tolist()

                    content[Id].update({"inShape":str(tmp).replace("'","")})

                # content[Id]={"inShape":str(extras_dict[jsonNetwork[Id]['backward_connections'][0]]) if len(jsonNetwork[Id]['backward_connections'])==1 else str([extras_dict[i] for i in jsonNetwork[Id]['backward_connections']]).replace("'","")}
                # content[Id].update({"inShape":value["inShape"]})

                if Id in lw_core.error_handler:
                    log.info("ErrorMessage: " + str(lw_core.error_handler[Id]))

                    content[Id]['Error'] = {
                        'Message': lw_core.error_handler[Id].error_message,
                        'Row': lw_core.error_handler[Id].error_line
                    }
                else:
                    content[Id]['Error'] = None
            
        elif action == "getNetworkOutputDim":
            jsonNetwork=request.get("value")

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)                        
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

        elif action == "getPreviewSample":
            value=request.get("value")
            jsonNetwork=value["Network"]
            LayerId=value["Id"]

            try:
                Variable=value["Variable"]
            except:
                Variable=None

            lw_core, extras_reader, data_container = self._create_lw_core(jsonNetwork, reciever)                                    
            lw_core.run()
            
            sample=""
            if Variable:
                dataContainerDict=data_container.to_dict()
                if LayerId in dataContainerDict:
                    sample = dataContainerDict[LayerId][Variable]
            else:
                extrasDict=extras_reader.to_dict()
                if LayerId in extrasDict:
                    sample = extrasDict[LayerId]["Sample"]

            if isinstance(sample,tf.Variable):
                sample=sample.numpy()

            if len(np.shape(sample))>1:
                sample=np.squeeze(sample)

            def reduceTo2d(data):
                data_shape=np.shape(np.squeeze(data))
                if len(data_shape)<=2 or (len(data_shape)==3 and (data_shape[-1]==3 or data_shape[-1]==1)):
                    return data
                else:
                    return reduceTo2d(data[...,-1])

            dataObject=createDataObject([reduceTo2d(np.asarray(sample))])
            
            if self._is_jsonable(dataObject):
                content = dataObject
            else:
                content = createDataObject([""])


        elif action == "getPreviewVariableList":
            value=request.get("value")
            jsonNetwork=value["Network"]
            LayerId=value["Id"]

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)                                                
            lw_core.run()
            
            extrasDict=extras_reader.to_dict()
            if LayerId in extrasDict:
                content = {
                    "VariableList": extrasDict[LayerId]["Variables"],
                    "VariableName": extrasDict[LayerId]["Default_var"],
                }

                if LayerId in lw_core.error_handler:
                    log.info("ErrorMessage: " + str(lw_core.error_handler[LayerId]))
                    
                    content['Error'] = {
                        'Message': lw_core.error_handler[LayerId].error_message,
                        'Row': lw_core.error_handler[LayerId].error_line
                    }
            else:
                content = ""
        
        ####################################Parser###################################
        elif action == "Parse":
            value=request.get("value")
            # Paths=value["Paths"]
            if value["Pb"]:
                pb=value["Pb"][0]
            else:
                pb=value["Pb"]

            if value["Checkpoint"]:
                ckpt=value["Checkpoint"][0]
            else:
                ckpt=value["Checkpoint"]

            Paths = [pb, ckpt]
            trainableFlag=value["Trainable"]
            end_points=value["EndPoints"]
            containers=value["Containers"]
            try:
                correct_file_list=self.getParsingFiles(Paths)
            except Exception as e:
                content=e
                print(e)

            filteredValueDict=None
            try:
                content, filteredValueDict=parse(trainableFlag, end_points, *correct_file_list)
            except Exception as e:
                print(traceback.format_exc())
                content="Could not parse the file.\n"+str(e)
                errorList.append("Could not parse the file")
            if type(filteredValueDict) is dict:
                self.checkpointDict[correct_file_list[-1]]=filteredValueDict
            else:
                warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
            
        ####################################Computing server#########################
        elif action == "Close":
            content="Shutting down app"
            self.shutDown()
            
            # for c in self.cores.values():
            #     content=c.Close()
            #     del c
            # sys.exit(1)

        elif action == "updateResults":
            content=core.updateResults()

        elif action == "checkCore":
            content=core.checkCore()

        elif action == "headless":
            value=request.get("value")
            if value:
                content=core.headlessOn()
            else:
                content=core.headlessOff()

        elif action == "getTrainingStatistics":
            value=request.get("value")
            content=core.getTrainingStatistics(value)

        elif action == "getTestingStatistics":
            value=request.get("value")
            content=core.getTestingStatistics(value)
        ################## Other ######################
        elif action == "getS3Keys":
            value = request.get("value")
            adapter = S3BucketAdapter(value['bucket'],
                                      value['aws_access_key_id'], value['aws_secret_access_key'])
            content = adapter.get_keys(value['delimiter'], value['prefix'])                    
        ################## Deprecated ######################
        elif action == "getLayerStatistics":
            value=request.get("value")
            result=core.getLayerStatistics(value)
            content=result

        elif action == "Start":
            network=request.get("value")
            for value in network['Layers'].values():
                if "checkpoint" in value and value["checkpoint"]:
                    self.add_to_checkpointDict(value)
            content=core.startCore(network, self.checkpointDict.copy())

        elif action=="startTest":
            content=core.startTest()

        elif action=="resetTest":
            content=core.resetTest()

        elif action =="getTestStatus":
            content=core.getTestStatus()

        elif action == "nextStep":
            content=core.nextStep()

        elif action == "previousStep":
            content=core.previousStep()

        elif action == "playTest":
            content=core.playTest()

        ################## OutDated ######################
        elif action == "getStatistics":
            value=request.get("value")
            content=core.getStatistics(value)

        elif action == "getIter":
            content=core.getIter()

        elif action == "getEpoch":
            content=core.getEpoch()

        elif action == "Stop":
            content=core.Stop()

        elif action == "Pause":
            content=core.Pause()

        elif action == "Unpause":
            content=core.Unpause()

        elif action == "SkipToValidation":
            content=core.skipToValidation()

        elif action == "Export":
            value=request.get("value")
            content=core.exportNetwork(value)

        elif action == "isTrained":
            content=core.isTrained()

        elif action == "SaveTrained":
            value=request.get("value")
            content=core.saveNetwork(value)

        elif action == "getEndResults":
            content=core.getEndResults()

        elif action == "getStatus":
            content=core.getStatus()

        else:
            warningList.append("Invalid action " + str(action))

        

        while not errors.empty():
            message=errors.get(timeout=0.05)
            errorList.append(message)

        while not warnings.empty():
            message=warnings.get(timeout=0.05)
            warningList.append(message)


        if errorList:
            core.Close()
            if not content:
                content={"content":"Core crashed without any error message, closing core"}
            try:
                content["errorMessage"]=errorList
            except:
                content={"content":content, "errorMessage":errorList}
        if warningList:
            try:
                content["warningMessage"]=warningList
            except:
                content={"content":content, "warningMessage":warningList}

        if type(content) is not dict:
            content={"content":content}
        elif type(content) is dict and "content" not in content:
            content={"content":content}

        endTime=time.time()

        print("Content before string: ", content)

        # if type(content).__name__=="str":
        #     content='"'+content+'"'

        response = {
            "length": len(json.dumps(content)),
            "body": content
        }

        response = json.dumps(response)

        test='{"length": '+str(len(str(content)))+', "body":'+str(content).replace("'",'"')+'}'

        print("Response: ", response)

        await websocket.send(response)

    def shutDown(self):
        for c in self.cores.values():
            content=c.Close()
            del c
        sys.exit(1)


cores=dict()
dataDict=dict()
checkpointDict=dict()
lwDict=dict()

path='0.0.0.0'
port=5000
interface=Message(cores, dataDict, checkpointDict, lwDict)
start_server = websockets.serve(interface.interface, path, port)
print("Trying to listen to: " + str(path) + " " + str(port))
connected=False
while not connected:
    try:
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        print("Connected")
        connected=True
    except KeyboardInterrupt:
        break
    # except SystemExit:
        # Might not want SystemExit since that will happen whenever someone closes the web browser
    #     break
    except:
        connected=False
    
