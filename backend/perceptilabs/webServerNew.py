import asyncio
import websockets
import ssl
import json
import struct
import io
import time
import traceback

from perceptilabs.coreLogic import coreLogic
from perceptilabs.propegateNetwork import lwNetwork
from perceptilabs.parse_pb import parse
import time
import numpy as np

from perceptilabs.dataKeeper import dataKeeper as lw_data
from perceptilabs.extractVariables import *
from perceptilabs.createDataObject import createDataObject

from perceptilabs.core_new.core import *
from perceptilabs.core_new.history import SessionHistory
from perceptilabs.core_new.errors import LightweightErrorHandler
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.core_new.lightweight import LightweightCore, LW_ACTIVE_HOOKS
from perceptilabs.graph import Graph
from perceptilabs.codehq import CodeHqNew as CodeHq
from perceptilabs.modules import ModuleProvider

import pprint
import logging

from perceptilabs.serverInterface import Interface

class Message:
    def __init__(self, cores, dataDict, checkpointDict):
        self.comInterface = Interface()

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
        value=request.get("value")

        self.comInterface.setCore(reciever)
        content = self.comInterface.create_response(action, value)

        response = {
            "length" : len(str(content)),
            "body": content
        }

        response = json.dumps(response)

        await websocket.send(response)
