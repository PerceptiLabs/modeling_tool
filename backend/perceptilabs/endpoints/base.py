import time
import logging

from flask_compress import Compress
from flask import Flask, request, g, jsonify, abort
from werkzeug.exceptions import HTTPException
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from perceptilabs.endpoints.network_data.base import NetworkData
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.endpoints.export.base import Export
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.issues import traceback_from_exception
import perceptilabs.utils as utils
import perceptilabs.endpoints.utils as endpoint_utils


logger = logging.getLogger(APPLICATION_LOGGER)

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

SENTRY_ENVIRONMENT = "production" if utils.is_prod() else "development"
SENTRY_RELEASE = utils.get_version() if utils.is_prod() else sentry_sdk.utils.get_default_release()

sentry_sdk.init(
    dsn="https://095ae2c447ec4da8809174aa9ce55906@o283802.ingest.sentry.io/5838672",
    integrations=[FlaskIntegration(), sentry_logging],
    environment=SENTRY_ENVIRONMENT,
    release=SENTRY_RELEASE    
)
logger.info(f"Initialized sentry for environment '{SENTRY_ENVIRONMENT}' and release '{SENTRY_RELEASE}'")


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
    return jsonify(endpoint_utils.is_valid_checkpoint_directory(directory))


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


@app.errorhandler(Exception)
def handle_endpoint_error(e):
    if isinstance(e, HTTPException):
        return e # pass through HTTP errors
    else:
        message = traceback_from_exception(e)
        logger.error(f"Error in request '{request.endpoint}'")
        abort(500, description=message)


