import time
import logging

from flask_cors import CORS
from flask_compress import Compress
from flask import Flask as _Flask, request, g, jsonify, abort, make_response, json
from flask.json import JSONEncoder as _JSONEncoder
from werkzeug.exceptions import HTTPException
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from perceptilabs.endpoints.version.base import Version
from perceptilabs.endpoints.network_data.base import NetworkData
from perceptilabs.endpoints.data.base import PutData, IsDataReady
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.endpoints.session.base import SessionStart, ActiveSessions, SessionProxy
from perceptilabs.endpoints.export.base import Export
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.issues import traceback_from_exception
from perceptilabs.endpoints.session.threaded_executor import ThreadedExecutor 
import perceptilabs.utils as utils
import perceptilabs.endpoints.utils as endpoint_utils


logger = logging.getLogger(APPLICATION_LOGGER)


if utils.is_prod() and not utils.is_pytest():
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

class JSONEncoder(_JSONEncoder):
    def default(self, obj):
        return utils.convert(obj)        
class Flask(_Flask):
    json_encoder = JSONEncoder

def create_app(data_metadata_cache=None, preview_cache=None, data_executor=None, session_executor=None):
    if data_executor is None:
        data_executor = utils.DummyExecutor()

    if session_executor is None:
        session_executor = ThreadedExecutor(single_threaded=True)
    
    app = Flask(__name__)
    cors = CORS(app, resorces={r'/d/*': {"origins": '*'}})
    
    compress = Compress()
    compress.init_app(app)

    app.add_url_rule(
        '/data',
        methods=['PUT'],
        view_func=PutData.as_view('put_data', data_executor, data_metadata_cache=data_metadata_cache) 
    )

    app.add_url_rule(
        '/data',
        methods=['GET'],
        view_func=IsDataReady.as_view('is_data_ready', data_metadata_cache=data_metadata_cache)
    ) 

    app.add_url_rule(
        '/model_recommendations',
        methods=['POST'],
        view_func=ModelRecommendations.as_view('model_recommendations', data_metadata_cache=data_metadata_cache)  
    )

    app.add_url_rule(
        '/network_data',
        methods=['POST'],
        view_func=NetworkData.as_view(
            'network_data', data_metadata_cache=data_metadata_cache, preview_cache=preview_cache)
    )

    app.add_url_rule(
        '/type_inference',
        methods=['GET'],
        view_func=TypeInference.as_view('type_inference')
    )

    app.add_url_rule(
        '/version',
        methods=['GET'],
        view_func=Version.as_view('version')
    )

    app.add_url_rule(
        '/layer_code',
        methods=['POST'],
        view_func=LayerCode.as_view('layer_code')
    )

    app.add_url_rule(
        '/session/start',
        methods=['POST'],
        view_func=SessionStart.as_view('session_start', session_executor)
    )

    app.add_url_rule(
        '/session/list',
        methods=['GET'],
        view_func=ActiveSessions.as_view('active_sessions', session_executor)
    )

    app.add_url_rule(
        '/session/proxy',
        methods=['POST'],
        view_func=SessionProxy.as_view('session_proxy', session_executor)
    )

    app.add_url_rule(
        '/export',
        methods=['POST'],
        view_func=Export.as_view('export', data_metadata_cache=data_metadata_cache)
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
        duration = time.perf_counter() - g.request_started
        logger.info(f"Request to endpoint '{request.endpoint}' took {duration:.4f}s")    
        return response
    
    @app.errorhandler(Exception)
    def handle_endpoint_error(e):
        message = traceback_from_exception(e)
        print(message)
        logger.exception(f"Error in request '{request.endpoint}'")
        return make_response(message), 500
    
    return app
