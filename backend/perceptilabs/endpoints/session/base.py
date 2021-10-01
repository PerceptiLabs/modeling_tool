import json
import logging
import requests
from flask import request, jsonify, abort, make_response
from flask.views import View

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.session.utils as session_utils


logger = logging.getLogger(APPLICATION_LOGGER)

class SessionStart(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Starts a training/testing session"""
        json_data = request.get_json()
        receiver = json_data.get('receiver')
        user_email = json_data.get('value').get('userEmail')

        action = json_data.get('action')
        logger.info(f"Session proxy called with action {action}")
        
        if action == "Start":
            task_type = 'training-session'
        elif action == "startTests":
            task_type = 'testing-session'
        else:
            raise ValueError("Unknown action to session start! Got: " + action)        

        session_id = self._executor.start_session(task_type, json_data)
        
        return jsonify({"content": "core started"})
    

def get_required_arg(request, name):
    arg = request.args.get(name)
    if not arg:
        abort(400, f"Missing {name} parameter")

    return arg


class SessionCancel(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Cancels a training/testing session"""
        user_email = get_required_arg(request, 'user_email')
        receiver = get_required_arg(request, 'receiver')

        def predicate(session_id, metadata):
            return (
                metadata['type'] in ['training-session', 'testing-session'] and
                metadata['payload']['value']['userEmail'] == user_email and
                str(metadata['payload']['receiver']) == str(receiver)
            )

        sessions_dict = self._executor.get_sessions(predicate=predicate)
        session_id = list(sessions_dict.keys())[0]
        self._executor.cancel_session(session_id, payload={'action': 'closeCore'})
        return jsonify({ "content": "Session canceled", })


class ActiveSessions(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Lists active training/testing sessions """
        user_email = get_required_arg(request, 'user_email')

        def predicate(session_id, metadata):
            return (
                metadata['type'] in ['training-session', 'testing-session'] and                
                metadata['payload']['value']['userEmail'] == user_email 
            )
        
        sessions_dict = self._executor.get_sessions(predicate=predicate)
        return jsonify(sessions_dict)

    
class SessionWorkers(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        workers = self._executor.get_workers()
        return jsonify(workers)

    
class SessionProxy(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        json_data = request.get_json()
        action = json_data.get('action')
        receiver = json_data.get('receiver')
        user_email = json_data.get('user_email')
        data = json_data.get('data')

        def predicate(session_id, metadata):
            return (
                metadata['type'] in ['training-session', 'testing-session'] and                
                metadata['payload']['value']['userEmail'] == user_email and
                str(metadata['payload']['receiver']) == str(receiver)
            )

        sessions_dict = self._executor.get_sessions(predicate=predicate)

        if sessions_dict:
            session_id = list(sessions_dict.keys())[0]
            resp = self._executor.send_request(session_id, data)
            return jsonify(resp)
        else:
            return jsonify({})
