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
from lw_data import lw_data
from parse_pb import parse
import time
from sentry_sdk import configure_scope
import numpy as np

from dataKeeper import dataKeeper as lw_data
from extractVariables import *
from createDataObject import createDataObject

from core_new.core import *
from core_new.history import SessionHistory
from core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
from graph import Graph
from codehq import CodeHqNew as CodeHq
from modules import ModuleProvider

import pprint
import logging

class Message:
    def __init__(self, cores, dataDict):
        self.cores=cores
        self.dataDict=dataDict


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
            core=coreLogic(reciever, self.dataDict[reciever])
            self.cores[reciever]=core
        else:
            core=self.cores[reciever]

        warnings=core.warningQueue
        warningList=[]

        errors=core.errorQueue
        errorList=[]

        content=""

        
        coreCalls=["Close", "updateResults", "checkCore", "headless", "getTrainingStatistics", "getTestingStatistics", "Start", "startTest", "resetTest", "getTestStatus",
        "nextStep", "previousStep", "playTest", "getIter", "getEpoch", "Stop", "Pause", "SkipToValidation", "Export", "getStatus"]
        lwCalls=["getDataPlot", "getDataMeta", "deleteData", "removeReciever", "getNetworkData", "getNetworkInputDim", "getNetworkOutputDim", "getPreviewSample"]
        parseCalls=["Parse"]
        with configure_scope() as scope:
            scope.set_extra("reciever",reciever)
            scope.set_extra("action",action)
            scope.set_extra("value",request.get("value"))
            #Check what the request is for and then get the properties needed for that function
            if action in coreCalls:
                # scope.set_extra("Core properties", core.core.__dict__)
                # coreProperties=dict()
                # for key, value in core.core.__dict__.items():
                #     if type(value).__name__!="dict":
                #         coreProperties[key]=value
                # scope.set_extra("Core properties", coreProperties)
                scope.set_extra("Saved Results Dict", core.savedResultsDict)
                scope.set_extra("Network", core.network)
            

            elif action in lwCalls:
                for dataId, dataValue in self.dataDict[reciever].items():
                    scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)
            elif action in parseCalls:
                pass
            else:
                # scope.set_extra("Core properties", core.core.__dict__)
                for dataId, dataValue in self.dataDict[reciever].items():
                    scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)

        #####################################B4End###################################
        if action == "getDataMeta":
            value=self.request.get("value")
            Id=value["Id"]
            jsonNetwork=value["Network"]

            lw_core, _, data_container = self._create_lw_core(jsonNetwork)
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
            value=self.request.get("value")
            Id=value["Id"]
            jsonNetwork=value["Network"]

            lw_core, _, data_container = self._create_lw_core(jsonNetwork)
            lw_core.run()

            def try_fetch(dict,variable):
                try:
                    return dict[variable]
                except:
                    return ""

            content=try_fetch(data_container[Id],"_partition_summary")


        elif action == "deleteData":
            value=self.request.get("value")
            if value["Id"] in self.dataDict[reciever]:
                del self.dataDict[reciever][value["Id"]]
                content={"content": "Deleted data on workspace " + str(reciever) + " with Id: " +str(value["Id"])+"."}
            else:
                content={"content": "No such Id had saved data in that workspace"}
            # print(self.dataDict)

        elif action == "removeReciever":
            for value in self.dataDict[reciever].values():
                del value
            del self.dataDict[reciever]
            # print(self.dataDict)
            content={"content": "All data on workspace " + str(reciever) + " has been deleted"}

        elif action == "getCode":
            value=self.request.get("value")
            Id=value["Id"]
            Type=value["Type"]
            Properties=value["Properties"]
            Con=value["backward_connections"]
            content={"Info":{"Type":Type, "Id": Id, "Properties": Properties}, "Con":Con}

            from codehq import CodeHqNew as CodeHq
            
            content = {"Output": CodeHq.get_code_generator(Id,content).get_code()}

        elif action == "getNetworkInputDim":
            jsonNetwork=self.request.get("value")
            
            pprint.pprint(jsonNetwork)

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)            
            lw_core.run()
            
            content={}
            # for Id, value in extras_reader.to_dict().items():
            #     inShape[Id]=value["inShape"]

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
                if "errorMessage" in extras_value:
                    print("ErrorMessage: ", extras_value['errorMessage'])
                    content[Id].update({"Error": extras_value['errorMessage']})
                    content[Id].update({"Row": extras_value['errorRow']})
                else:
                    content[Id].update({"Error": None})
                    content[Id].update({"Row": None})

            
        elif action == "getNetworkOutputDim":
            jsonNetwork=self.request.get("value")

            
            pprint.pprint(jsonNetwork)

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)                        
            lw_core.run()
            
            extrasDict=extras_reader.to_dict()

            content={}

            for Id, value in extrasDict.items():
                content[Id]={}
                content[Id].update({"Dim": str(value["outShape"]).replace("[","").replace("]","").replace(", ","x")})
                if "errorMessage" in value:
                    print("ErrorMessage: ", value['errorMessage'])
                    content[Id].update({"Error": value['errorMessage']})
                    content[Id].update({"Row": value['errorRow']})
                else:
                    content[Id].update({"Error": None})
                    content[Id].update({"Row": None})


        elif action == "getPreviewSample":
            value=self.request.get("value")
            jsonNetwork=value["Network"]
            LayerId=value["Id"]

            try:
                Variable=value["Variable"]
            except:
                Variable=None

            lw_core, extras_reader, data_container = self._create_lw_core(jsonNetwork)                                    
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
                content = ""



        elif action == "getPreviewVariableList":
            value=self.request.get("value")
            jsonNetwork=value["Network"]
            LayerId=value["Id"]

            lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)                                                
            lw_core.run()
            
            extrasDict=extras_reader.to_dict()
            if LayerId in extrasDict:
                content = {
                    "VariableList": extrasDict[LayerId]["Variables"],
                    "VariableName": extrasDict[LayerId]["Default_var"],
                }
                if "errorMessage" in extrasDict[LayerId]:
                    content.update({"Error": extrasDict[LayerId]['errorMessage']})
                    content.update({"Row": extrasDict[LayerId]['errorRow']})
            else:
                content = ""
        
        ####################################Parser###################################
        elif action == "Parse":
            value=self.request.get("value")
            Paths=value["Paths"]
            trainableFlag=value["Trainable"]
            end_points=value["EndPoints"]
            try:
                containers=value["Containers"]
            except:
                pass
            # Paths=value
            # trainableFlag="All"
            # end_points=""
            correct_file_list=self.getParsingFiles(Paths)
            # if correct_file_list[-1] not in self.checkpointDict:
            #     self.checkpointDict[correct_file_list[-1]]=extractCheckpointInfo(*correct_file_list)
            # try:
            print("Files: " , correct_file_list)
            filteredValueDict=None
            try:
                content, filteredValueDict=parse(trainableFlag, end_points, *correct_file_list)
            except Exception as e:
                print(traceback.format_exc())
                content="Could not parse the file.\n"+str(e)
            if type(filteredValueDict) is dict:
                self.checkpointDict[correct_file_list[-1]]=filteredValueDict
            else:
                warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
            

            # except Exception as e:
            #     print("Error: ", e)
            #     content={"content":"Parser crashed"}
            #     errors.put("Parser crashed")

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
            value=self.request.get("value")
            if value:
                content=core.headlessOn()
            else:
                content=core.headlessOff()

        elif action == "getTrainingStatistics":
            value=self.request.get("value")
            content=core.getTrainingStatistics(value)

        elif action == "getTestingStatistics":
            value=self.request.get("value")
            content=core.getTestingStatistics(value)
        ################## Other ######################
        elif action == "getS3Keys":
            value = self.request.get("value")
            adapter = S3BucketAdapter(value['bucket'],
                                        value['aws_access_key_id'], value['aws_secret_access_key'])
            content = adapter.get_keys(value['delimiter'], value['prefix'])                    
        ################## Deprecated ######################
        elif action == "getLayerStatistics":
            value=self.request.get("value")
            result=core.getLayerStatistics(value)
            content=result

        elif action == "Start":
            value=self.request.get("value")
            content=core.startCore(value)

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
            value=self.request.get("value")
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
            value=self.request.get("value")
            content=core.exportNetwork(value)

        elif action == "isTrained":
            content=core.isTrained()

        elif action == "SaveTrained":
            value=self.request.get("value")
            content=core.saveNetwork(value)

        elif action == "getStatus":
            answer=core.getStatus()
            content=answer

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

        if type(content).__name__=="str":
            content='"'+content+'"'

        response='{"length":'+str(len(str(content)))+',"body":'+str(content).replace("'",'"')+'}'

        response=str(response)

        # print("Response: "+str(response))
        await websocket.send(response)

    def shutDown(self):
        for c in self.cores.values():
            content=c.Close()
            del c
        sys.exit(1)


cores=dict()

path='0.0.0.0'
port=5000
start_server = websockets.serve(interface, path, port)
print("Trying to listen to: " + str(path) + " " + str(port))
connected=False
while not connected:
    try:
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        print("Connected")
        connected=True
    except:
        connected=False

    
