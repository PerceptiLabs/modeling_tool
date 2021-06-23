import time
import logging

from flask_compress import Compress
from flask import Flask, request, g

from perceptilabs.endpoints.network_data.base import NetworkData
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

app = Flask(__name__)

compress = Compress()
compress.init_app(app)


app.add_url_rule(
    '/model_recommendations',
    methods=['POST'],
    view_func=ModelRecommendations().as_view('model_recommendations')
)


app.add_url_rule(
    '/network_data',
    methods=['POST'],
    view_func=NetworkData().as_view('network_data')
)


app.add_url_rule(
    '/type_inference',
    methods=['GET'],
    view_func=TypeInference().as_view('type_inference')
)


app.add_url_rule(
    '/layer_code',
    methods=['POST'],
    view_func=LayerCode().as_view('layer_code')
)


def healthy():
    return '{"healthy": "true"}'


app.add_url_rule(
    '/health',
    methods=['GET'],
    view_func=healthy
)

@app.before_request
def before_request():
    g.request_started = time.perf_counter()
    

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')

    duration = time.perf_counter() - g.request_started
    logger.info(f"Request to endpoint '{request.endpoint}' took {duration}s")    
    
    return response


