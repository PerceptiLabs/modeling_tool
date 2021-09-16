import json
import logging
import requests
from flask.views import View
from flask import request, Response, jsonify, make_response
import requests


from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.session.utils as session_utils
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
            task_start_info = self._executor.start_task(
                'serve-gradio', user_email, model_id, payload)
        else:
            raise NotImplementedError("No serving type called '{serving_type}'")
            
        return jsonify({
            "content": "serving started",
            **task_start_info
        })


class IsServedModelReady(View):
    def __init__(self, executor):
        self._executor = executor

    def dispatch_request(self):
        model_id = request.args['model_id']
        user_email = request.args['user_email']        

        url = self._executor.send_request(
            user_email, model_id, 'get_url', {'action': 'get_url'})

        if url:
            return jsonify(f"Model served via Gradio at {url}")            
        else:
            return make_response('', 204)

