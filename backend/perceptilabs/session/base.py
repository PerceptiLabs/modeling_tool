from abc import ABC, abstractmethod
import asyncio
import logging
import requests
from abc import ABC, abstractmethod

import threading
import time
import json

import numpy as np
import aiohttp
import aiohttp.web


import perceptilabs.settings as settings
import perceptilabs.utils as utils
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


class BaseExecutor(ABC):  
    @abstractmethod
    def is_available(self):
        raise NotImplementedError
    
    @abstractmethod
    def start_session(self, session_type, payload):
        raise NotImplementedError

    @abstractmethod
    def get_session_meta(self, session_id):        
        raise NotImplementedError

    @abstractmethod
    def get_session_hostname(self, session_id):        
        raise NotImplementedError

    @abstractmethod
    def cancel_session(self, session_id, payload=None):
        raise NotImplementedError

    @abstractmethod
    def get_workers(self):
        raise NotImplementedError

    @abstractmethod
    def get_sessions(self, predicate=None):
        raise NotImplementedError

    def send_request(self, session_id, payload):
        metadata = self.get_session_meta(session_id)
        
        if not metadata:
            return {}

        try:
            host = metadata['hostname']
            port = metadata['port']
            url = f'http://{host}:{port}/'
            response = requests.post(url, json=payload, timeout=5)  # Forward request to worker
            if response.ok:
                return response.json()
            else:
                raise Exception(f"Received status code {response.status_code} from {url}")
        except requests.exceptions.ReadTimeout as e:
            raise Exception(f"Timeout while waiting for the result from the session thread. Request: {payload}")
        except Exception as e:
            logger.exception(e)
            raise e

    
class Session(ABC):
    @abstractmethod
    def on_request_received(self, payload):
        raise NotImplementedError

    @abstractmethod
    def on_start_called(self, payload, is_retry):
        raise NotImplementedError

    def start(self, start_payload, is_retry, on_task_started, cancel_token=None):
        self.on_start_called(start_payload, is_retry)

        async def handle_request(request):
            request_data = await request.json()
            response_data = self.on_request_received(request_data)
            
            return aiohttp.web.json_response(
                response_data, dumps=lambda x: json.dumps(x, default=utils.convert))

        app = aiohttp.web.Application()
        app.router.add_post('/', handle_request)
    
        async def run():
            port = utils.find_free_port_in_range(
                settings.TRAINING_PORT_MIN,
                settings.TRAINING_PORT_MAX)
    
            runner = aiohttp.web.AppRunner(app)
            await runner.setup()
            site = aiohttp.web.TCPSite(runner, port=port)
            await site.start()

            if on_task_started:
                on_task_started(start_payload, port)

            while not self.has_finished:
                await asyncio.sleep(1)

            if self.has_failed:
                raise RuntimeError("Task failed!")
    
            # hack to leave the thread running until the frontend can get the last updates from the api
            # The correct way would be to call all of the endpoints from which the frontend will  need final information

            if cancel_token:
                # the cancel_token is thread-based instead of asyncio, so we can't just call wait(timeout=60) without halting the webserver we're running in this thread
                for _ in range(60):
                    if cancel_token.wait(timeout=0.01):
                        break
                    await asyncio.sleep(1)
            else:
                await asyncio.sleep(10)                

            logging.info("Shutting down task http server...")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run())
        
    @property
    def has_finished(self):
        return False

    @property
    def has_failed(self):
        return False
    
