import json
import logging
import requests
from flask import request, jsonify
from flask.views import View

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.session.utils as session_utils


logger = logging.getLogger(APPLICATION_LOGGER)


class SessionStart(View):
    def __init__(self, executor):
        self._executor = executor
    
    def dispatch_request(self):
        json_data = request.get_json()
        receiver = json_data.get('receiver')
        user_email = json_data.get('value').get('userEmail')
        session_id = self._executor.start_task(user_email, receiver, json_data)
        return jsonify({"content": "core started"})            


class ActiveSessions(View):
    def __init__(self, executor):
        self._executor = executor
    
    def dispatch_request(self):
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
        
        try:
            port = info['port']
            path = f'http://localhost:{port}/'
            response = requests.post(path, json=data)  # Forward request to worker
            logger.info(f"Forwarded action '{action}' to receiver '{receiver}' at '{path}'")
            return jsonify(response.json())
        except:
            return jsonify({})
        
    
