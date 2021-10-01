import json
import logging
import requests
from flask.views import View
from flask import request, Response, jsonify, make_response
import requests


from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.session.utils as session_utils
import perceptilabs.utils as utils


logger = logging.getLogger(APPLICATION_LOGGER)


class ServingStart(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        """ Starts a training/testing session"""

        if utils.is_docker():
            return jsonify({'error': 'serving is not implemented for the docker version'})
        
        json_data = request.get_json()

        serving_type = json_data.get('type')        
        payload = json_data.get('payload')

        model_id = json_data.get('modelId')
        user_email = json_data.get('userEmail')

        if serving_type == "gradio":
            self._executor.start_session('gradio-session', payload)            
        else:
            raise NotImplementedError("No serving type called '{serving_type}'")
            
        return jsonify({"content": "serving started"})
    

class IsServedModelReady(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        model_id = request.args['model_id']
        user_email = request.args['user_email']        


        def predicate(session_id, metadata):
            return (
                metadata['type'] in ['gradio-session'] and                
                metadata['payload']['userEmail'] == user_email and
                str(metadata['payload']['modelId']) == str(model_id)
            )

        sessions_dict = self._executor.get_sessions(predicate=predicate)

        if sessions_dict:
            session_id = list(sessions_dict.keys())[0]
            url = self._executor.send_request(session_id, {'action': 'get_url'})
            
            if url:
                return jsonify(f"Model served via Gradio at {url}")

        return make_response('', 204)
            

class Models(View):  # TODO: replace the above two w/ this...
    def __init__(self, executor):
        self._executor = executor
    
    def dispatch_request(self, model_id):
        user_email = request.args['user_email']  # TODO: make this a cookie, see https://stackoverflow.com/questions/4024271/rest-api-best-practices-where-to-put-parameters


        def predicate(session_id, metadata):
            return (
                metadata['type'] in ['gradio-session'] and                
                metadata['payload']['userEmail'] == user_email
            )

        sessions_dict = self._executor.get_sessions(predicate=predicate)
        return jsonify(sessions_dict)

            

        

            
            


        
