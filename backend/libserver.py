import sys
import selectors
import json
import io
import os
import struct
import traceback
from coreLogic import coreLogic
# from propegateNetwork import lwNetwork
from parse_pb import parse
import time
from sentry_sdk import configure_scope
import numpy as np
import skimage
# from datahandler_lw import DataHandlerLW
# from lw_data import lw_data
# from dataKeeper import dataKeeper as lw_data
from createDataObject import createDataObject

from core_new.core import *
from core_new.history import SessionHistory
from core_new.cache import get_cache
from core_new.errors import LightweightErrorHandler
from core_new.extras import LayerExtrasReader
from core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
from graph import Graph
from codehq import CodeHqNew as CodeHq
from modules import ModuleProvider
from core_new.networkCache import NetworkCache

import pprint
import logging
log = logging.getLogger(__name__)


class Message:
    def __init__(self, selector, sock, addr, interface):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self._interface = interface

        
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

    # def getParsingFiles(self,fileList):
    #     # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/graph.pbtxt' #path to your .pbtxt file
    #     # # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/frozen_inference_graph.pb'
    #     # checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/model.ckpt-51249'
    #     # return [graph_def_path,checkpoint]
    #     if fileList[1]=="" and "." not in fileList[0].split("/")[-1]:
    #         #Then its a folder
    #         return ""
    #     elif fileList[1]=="":
    #         if ".pb" in fileList[0]:
    #             return [fileList[0],None]
    #         else:
    #             raise Exception("Only frozen .pb files can be parsed by themselves")
    #     else:
    #         graph_def_path=""
    #         checkpoint=""
    #         for _file in fileList:
    #             if ".ckpt" in _file:
    #                 path, fileName=os.path.split(_file)
    #                 if "ckpt" in fileName.split(".")[-1]:
    #                     checkpoint=_file
    #                 else:
    #                     newFileName=".".join(fileName.split(".")[0:-1])
    #                     checkpoint=os.path.abspath(os.path.join(path, newFileName))
                    
    #             elif any([pb in _file for pb in [".pb", ".pbtxt"]]):
    #                 graph_def_path=_file
    #             else:
    #                 raise Exception("File type not recognised")
    #         if graph_def_path and checkpoint:
    #             return [graph_def_path, checkpoint]
    #         else:
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

    # def add_to_checkpointDict(self, content):
    #     if content["checkpoint"][-1] not in self.checkpointDict:
    #         from extractVariables import extractCheckpointInfo
    #         ckptObj=extractCheckpointInfo(content["endPoints"], *content["checkpoint"])
    #         self.checkpointDict[content["checkpoint"][-1]]=ckptObj.getVariablesAndConstants()
    #         ckptObj.close()

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

    # def _delete_lw_cach(self, reciever):
    #     del self.lwDict[reciever]

    def _create_response_json_content(self):
        # try:
        #     return interface
        # except:
        #     return error
        # reciever=self.request.get("reciever")
        # action = self.request.get("action")

        response, warnings, errors = self._interface.create_response(request)


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
        log.info("closing connection to {}".format(self.addr))
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
    
    # def shutDown(self):
    #     for c in self.cores.values():
    #         c.Close()
    #         del c
    #     sys.exit(1)
