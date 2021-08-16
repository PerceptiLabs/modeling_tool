import aiohttp
import aiohttp.web
import asyncio
import logging
import numpy as np
import threading
import time
import json
import socket
from contextlib import closing


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


def run_kernel(start_payload, on_server_started=None, is_retry=False, cancel_token=None):
    from perceptilabs.mainInterface import Interface
    from perceptilabs.issues import IssueHandler
    from flask import Flask, request, jsonify

    issue_handler = IssueHandler()
    cores = dict()
    testcore = None
    dataDict = dict()
    lwDict = dict()
    interface = Interface(cores, testcore, dataDict, lwDict, issue_handler, session_id='123', allow_headless=False)

    global has_finished, has_failed
    has_finished = False
    has_failed = False

    def on_finished(failed=False):
        global has_finished, has_failed
        has_finished = True
        has_failed = failed

    interface.create_response(start_payload, is_retry=is_retry, on_finished=on_finished)  # Start training

    async def handle_request(request):
        request_data = await request.json()
        response_data = interface.create_response_with_errors(request_data)
        return aiohttp.web.json_response(
            response_data, dumps=lambda x: json.dumps(x, default=convert))

    app = aiohttp.web.Application()
    app.router.add_post('/', handle_request)

    async def run():
        # TODO jon: this isn't always localhost.
        hostname = 'localhost'
        port = find_free_port_in_range(
            settings.TRAINING_PORT_MIN, settings.TRAINING_PORT_MAX)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, port=port)
        await site.start()

        on_server_started(hostname, port)

        global has_finished, has_failed

        while not has_finished:
            await asyncio.sleep(1)

        if has_failed:
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
