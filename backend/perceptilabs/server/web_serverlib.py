import asyncio
import ssl
import json
import struct
import io
import os

import pprint
import logging

log = logging.getLogger(__name__)

class Message:
    def __init__(self, interface):
        self.request = None
        self._jsonheader_len = None
        self.jsonheader = None
        self._interface = interface

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
            log.info("received" + str(self.jsonheader["content-type"]) + " request from")

    def _add_errors_and_warnings(self, content, issue_handler):
        errorList = issue_handler.pop_errors()
        warningList = issue_handler.pop_warnings()

        if errorList:
            self._interface.close_core(self.request.get("reciever"))
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
        
        return content

    async def interface(self, websocket, path):
        self.request = await websocket.recv()
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
            "length": len(json.dumps(content)),
            "body": content
        }

        response = json.dumps(response)

        await websocket.send(response)


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
    
