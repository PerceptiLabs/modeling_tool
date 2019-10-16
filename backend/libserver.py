import sys
import selectors
import json
import io
import os
import struct
import traceback
from coreLogic import coreLogic
from propegateNetwork import lwNetwork
from parse_pb import parse
import time
from sentry_sdk import configure_scope
import numpy as np
# from datahandler_lw import DataHandlerLW
# from lw_data import lw_data
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
log = logging.getLogger(__name__)

class Message:
    def __init__(self, selector, sock, addr, cores, dataDict, checkpointDict, lwNetworks):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

        self.cores=cores
        self.dataDict=dataDict
        self.checkpointDict=checkpointDict
        self.lwNetworks=lwNetworks

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError as e:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        except ConnectionResetError:
            self.shutDown()
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            #print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                # print("*"*50)
                # print(self._send_buffer)
                # print("*"*50)
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError as e:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                print(e)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    # def _create_message(
    #     self, *, content_bytes, content_type, content_encoding
    # ):
    #     jsonheader = {
    #         "byteorder": sys.byteorder,
    #         "content-type": content_type,
    #         "content-encoding": content_encoding,
    #         "content-length": len(content_bytes),
    #     }
    #     jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
    #     message_hdr = struct.pack(">H", len(jsonheader_bytes))
    #     message = message_hdr + jsonheader_bytes + content_bytes
    #     return message

    def getParsingFiles(self,fileList):
        # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/graph.pbtxt' #path to your .pbtxt file
        # # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/frozen_inference_graph.pb'
        # checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/model.ckpt-51249'
        # return [graph_def_path,checkpoint]
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

    def _create_message(self, *, content):
        content_bytes=self._json_encode(content, "utf-8")
        # json= "length:"+str(len(content_bytes))+" body:"+str(content)
        json = {
            "length": len(content_bytes),
            "body":content            
        }
        json_bytes = self._json_encode(json, "utf-8")
        message = json_bytes
        return message

    def _is_jsonable(self, x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def _create_lw_core(self, jsonNetwork):
        graph = Graph(jsonNetwork)
        
        graph_dict = graph.graphs
        data_container = DataContainer()
        
        session_history_lw = SessionHistory()
        extras_reader = LayerExtrasReader()

        from codehq import CodeHqNew as CodeHq

        module_provider = ModuleProvider()
        module_provider.load('tensorflow', as_name='tf')
        module_provider.load('numpy', as_name='np')
        module_provider.load('gym')
        
        for hook_target, hook_func in LW_ACTIVE_HOOKS.items():
            module_provider.install_hook(hook_target, hook_func)
            
        lw_core = LightweightCore(CodeHq, graph_dict,
                                  data_container, session_history_lw,
                                  module_provider, extras_reader)
        
        return lw_core, extras_reader, data_container

    def _create_response_json_content(self):
        reciever=self.request.get("reciever")
        action = self.request.get("action")
        startTime=time.time()

        #Check if the core exists, otherwise create one
        

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
            scope.set_extra("value",self.request.get("value"))
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
            print("VALUE: ", value)
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

            for Id, value in extras_reader.to_dict().items():
                content[Id]={}
                content[Id].update({"inShape":value["inShape"]})
                if "errorMessage" in value:
                    print("ErrorMessage: ", value['errorMessage'])
                    content[Id].update({"Error": value['errorMessage']})
                    content[Id].update({"Row": value['errorRow']})
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
                    content.update({"Error": value['errorMessage']})
                    content.update({"Row": value['errorRow']})
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

        response = {
            "content": content
        }
        log.debug("Response: " + pprint.pformat(response, depth=6))        
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)

            log.info("received request {} from {}".format(pprint.pformat(self.request), self.addr))
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        # try:
        message = self._create_message(**response)
        # except Exception as e:
        #     print(response)
        #     print(e)
        self.response_created = True
        self._send_buffer += message
    
    def shutDown(self):
        for c in self.cores.values():
            content=c.Close()
            del c
        sys.exit(1)
