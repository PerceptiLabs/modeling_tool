import time
import logging

from flask_compress import Compress
from flask import Flask, request, g, jsonify

from perceptilabs.endpoints.network_data.base import NetworkData
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.endpoints.export.base import Export
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.utils as utils


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


app.add_url_rule(
    '/export',
    methods=['POST'],
    view_func=Export().as_view('export')
)


@app.route('/healthy', methods=['GET'])
def healthy():
    return '{"healthy": "true"}'


@app.route('/has_checkpoint', methods=['GET'])
def has_checkpoint():
    directory = request.args.get('directory')
    return jsonify(utils.is_valid_checkpoint_directory(directory))


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


