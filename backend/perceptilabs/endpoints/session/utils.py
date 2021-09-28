import asyncio
import logging
import socket
from abc import ABC, abstractmethod
from contextlib import closing

import threading
import time
import json

import numpy as np
import aiohttp
import aiohttp.web


import perceptilabs.settings as settings
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

def convert(o):
    if isinstance(o, np.int64):
        return int(o)
    elif isinstance(o, np.float64):
        return float(o)
    elif isinstance(o, np.float32):
        return float(o)
    raise TypeError


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def find_free_port_in_range(min_port, max_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = min_port
    while port <= max_port:
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError('no free ports')


class Session(ABC):
    @abstractmethod
    def on_request_received(self, payload):
        raise NotImplementedError

    @abstractmethod
    def on_start_called(self, payload, is_retry):
        raise NotImplementedError

    def start(self, start_payload, is_retry, on_task_started, cancel_token):
        self.on_start_called(start_payload, is_retry)
        
        async def handle_request(request):
            request_data = await request.json()

            response_data = self.on_request_received(request_data)
            return aiohttp.web.json_response(
                response_data, dumps=lambda x: json.dumps(x, default=convert))
    
        app = aiohttp.web.Application()
        app.router.add_post('/', handle_request)
    
        async def run():
            port = find_free_port_in_range(
                settings.TRAINING_PORT_MIN,
                settings.TRAINING_PORT_MAX)
    
            runner = aiohttp.web.AppRunner(app)
            await runner.setup()
            site = aiohttp.web.TCPSite(runner, port=port)
            await site.start()

            if on_task_started:
                on_task_started(port)
    
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
                await asyncio.sleep(60)
    
            logging.info("Shutting down task http server...")
    
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run())
        
    @property
    def has_finished(self):
        return False

    @property
    def has_failed(self):
        return False
    
    @staticmethod
    def from_type(task_type):
        if task_type == 'start-training':
            return TrainingSession()
        elif task_type == 'start-testing':
            return TestingSession()
        elif task_type == 'serve-gradio':
            from perceptilabs.serving.gradio_serving import GradioSession
            return GradioSession()
        else:
            raise ValueError("Unknown task type: " + str(task_type))


# TODO: move TestingSession&TrainingSession into some better location
        
from perceptilabs.mainInterface import Interface
from perceptilabs.issues import IssueHandler

class TestingSession(Session):
    def __init__(self):
        self._has_finished = False
        self._has_failed = False

        issue_handler = IssueHandler()
        cores = dict()
        testcore = None
        
        self._main_interface = Interface(
            cores, testcore, issue_handler,
            session_id='123', allow_headless=False)
    
    def on_request_received(self, request):
        response = self._main_interface.create_response_with_errors(request)        
        return response
    
    def on_start_called(self, start_payload, is_retry):
        def on_finished(failed=False):
            self._has_finished = True
            self._has_failed = failed

        self._main_interface.create_response(
            start_payload, is_retry=is_retry, on_finished=on_finished)  # Start training/testing

    @property
    def has_finished(self):
        return self._has_finished

    @property
    def has_failed(self):
        return self._has_failed
        
        
TrainingSession = TestingSession  # TODO(anton.k): decouple and simplify!


def get_threaded_session_executor():
    from perceptilabs.endpoints.session.threaded_executor import ThreadedExecutor
    return ThreadedExecutor(single_threaded=False)

def get_session_executor():
    from perceptilabs.endpoints.session.celery_executor import CeleryExecutor

    if settings.CELERY:
        logger.info("Using Celery executor for training/testing tasks...")
        return CeleryExecutor()
    else:
        logger.info("Using Threaded executor for training/testing tasks...")
        return get_threaded_session_executor()
