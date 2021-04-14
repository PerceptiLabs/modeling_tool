import asyncio
import ssl
import json
import struct
import io
import os
import logging
import pprint
import numpy as np

from perceptilabs.utils import RateCounter
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)

def convert(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


class Message:
    def __init__(self, interface):
        self.request = None
        self._jsonheader_len = None
        self.jsonheader = None
        self._interface = interface

        if logger.isEnabledFor(logging.DEBUG):                
            self._bytes_in = RateCounter(window=3)
            self._bytes_out = RateCounter(window=3)        

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def process_protoheader(self):
        hdrlen = 2
        if len(self.request) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self.request[:hdrlen]
            )[0]
            self.request = self.request[hdrlen:]
        # return (request,_jsonheader_len)

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self.request) >= hdrlen:
            self.jsonheader = self._json_decode(
                self.request[:hdrlen], "utf-8"
            )
            self.request = self.request[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError("Missing required header " + reqhdr)

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self.request) >= content_len:
            return
        data = self.request[:content_len]
        self.request = self.request[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
        else:
            # Binary or unknown content-type
            self.request = data
            logger.info("received" + str(self.jsonheader["content-type"]) + " request from")

    def _add_errors_and_warnings(self, content, issue_handler):
        errorList = issue_handler.pop_errors()
        warningList = issue_handler.pop_warnings()
        logList = issue_handler.pop_logs()
        infoList = issue_handler.pop_info()
        
        if errorList:
            self._interface.close_core(self.request.get("receiver"))
            if type(content) is dict and "content" in list(content.keys()):
                content["errorMessage"]=errorList
            else:
                content={"content":content, "errorMessage":errorList}

        if warningList:
            if type(content) is dict and "content" in list(content.keys()):
                content["warningMessage"]=warningList
            else:
                content={"content":content, "warningMessage":warningList}

        if logList:
            if type(content) is dict and "content" in list(content.keys()):
                content["consoleLogs"]=logList
            else:
                content={"content":content, "consoleLogs":logList}
        
        if infoList:
            if type(content) is dict and "content" in list(content.keys()):
                content["generalLogs"]=infoList
            else:
                content={"content":content, "generalLogs":infoList}
        
        return content

    async def interface(self, websocket, path):
        self.request = await websocket.recv()

        if logger.isEnabledFor(logging.DEBUG):                
            self._bytes_in.add_entry(value=len(self.request))
        
        self.process_protoheader()
        self.process_jsonheader()
        self.process_request()

        response, issue_handler = self._interface.create_response(self.request)
        content = self._add_errors_and_warnings(response, issue_handler)

        if type(content) is not dict:
            content={"content":content}
        elif type(content) is dict and "content" not in content:
            content={"content":content}

        response = {
            "length": len(json.dumps(content, default=convert)),
            "body": content
        }

        response = json.dumps(response, default=convert)

        await websocket.send(response)
        
        if logger.isEnabledFor(logging.DEBUG):        
            self._bytes_out.add_entry(value=len(response))
            logger.debug(f'Bytes in per/s: {self._bytes_in.get_average_value()}. Requests per second {self._bytes_in.get_average_count()}')
            logger.debug(f'Bytes out per/s: {self._bytes_out.get_average_value()}. Responses per second {self._bytes_out.get_average_count()}')                    


# import logging        

# logging.basicConfig(stream=sys.stdout,
#                     format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
#                     level=logging.INFO)

# cores=dict()
# dataDict=dict()
# checkpointDict=dict()

# path='0.0.0.0'
# port=5000
# interface=Message(cores, dataDict, checkpointDict)
# start_server = websockets.serve(interface.interface, path, port)
# print("Trying to listen to: " + str(path) + " " + str(port))
# print("Test3")
# # asyncio.get_event_loop().run_until_complete(start_server)
# # asyncio.get_event_loop().run_forever()


# connected=False
# while not connected:
#     try:
#         print("Connected")
#         asyncio.get_event_loop().run_until_complete(start_server)
#         asyncio.get_event_loop().run_forever()
#         connected=True
#     except:
#         connected=False
    
