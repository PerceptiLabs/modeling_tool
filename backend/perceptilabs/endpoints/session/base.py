import json
import logging
import requests
from flask import request, jsonify, abort
from flask.views import View

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.session.utils as session_utils


logger = logging.getLogger(APPLICATION_LOGGER)

class SessionStart(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Starts a training/testing session"""
        json_data = request.get_json()
        receiver = json_data.get('receiver')
        user_email = json_data.get('value').get('userEmail')
        task_start_info = self._executor.start_task(user_email, receiver, json_data)
        return jsonify({
            "content": "core started",
            **task_start_info
        })


class SessionCancel(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Cancels a training/testing session"""
        if not request.args.get('user_email'):
            abort(400, "Missing user_email parameter")
        if not request.args.get('receiver'):
            abort(400, "Missing receiver parameter")

        user_email = request.args['user_email']
        receiver = request.args['receiver']
        task_start_info = self._executor.cancel_task(user_email, receiver)
        return jsonify({ "content": "Session canceled", })


class ActiveSessions(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Lists active training/testing sessions """
        if request.args.get('user_email'):
            user_email = request.args['user_email']
            tasks_dict = self._executor.get_active_tasks(user_email)
        return jsonify(tasks_dict)


class SessionProxy(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        json_data = request.get_json()
        action = json_data.get('action')
        receiver = json_data.get('receiver')
        user_email = json_data.get('user_email')
        data = json_data.get('data')        

        info = self._executor.get_task_info(user_email, receiver)

        if not info:
            return jsonify({})

        try:
            port = info['port']
            # TODO jon: get host from session. If threaded then localhost if celery, then from the task info.
            path = f'http://localhost:{port}/'
            response = requests.post(path, json=data, timeout=5)  # Forward request to worker
            return jsonify(response.json())
        except requests.exceptions.ReadTimeout as e:
            return abort(500, f"Timeout while waiting for the result of action '{action}' from the training thread. Request: {request}")
        except Exception as e:
            logger.exception(e)
            return abort(500)
