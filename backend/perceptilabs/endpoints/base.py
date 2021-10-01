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

from perceptilabs.resources.models import ModelAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.caching.utils import NullCache
from perceptilabs.endpoints.version.base import Version
from perceptilabs.endpoints.network_data.base import NetworkData, Previews
from perceptilabs.endpoints.data.base import PutData, IsDataReady
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.endpoints.session.base import SessionStart, ActiveSessions, SessionProxy, SessionCancel, SessionWorkers
from perceptilabs.endpoints.serving.base import ServingStart, IsServedModelReady, Models
from perceptilabs.endpoints.export.base import Export
from perceptilabs.endpoints.set_user.base import SetUser
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.issues import traceback_from_exception
from perceptilabs.session.threaded_executor import ThreadedExecutor
from perceptilabs.resources.epochs import EpochsAccess
import perceptilabs.utils as utils
import perceptilabs.session.utils as session_utils


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

def create_app(
        data_metadata_cache = NullCache(),
        preview_cache = NullCache(),
        data_executor = utils.DummyExecutor(),
        session_executor = session_utils.get_threaded_session_executor(single_threaded=True)
):
    app = Flask(__name__)
    cors = CORS(app, resorces={r'/d/*': {"origins": '*'}})

    compress = Compress()
    compress.init_app(app)

    model_access = ModelAccess(ScriptFactory())
    epochs_access = EpochsAccess()

    app.add_url_rule(
        '/set_user',
        methods=['POST'],
        view_func=SetUser.as_view('set_user')
    )

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
            'network_data',
            model_access,
            data_metadata_cache=data_metadata_cache, preview_cache=preview_cache
        )
    )

    previews_view = Previews.as_view(
        'previews',
        model_access,
        data_metadata_cache=data_metadata_cache,
        preview_cache=preview_cache
    )
    app.add_url_rule(
        '/previews', methods=['POST'], defaults={'layer_id': None}, view_func=previews_view)
    app.add_url_rule(
        '/previews/<layer_id>', methods=['POST'], view_func=previews_view)
    
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
        view_func=LayerCode.as_view('layer_code', model_access)
    )

    app.add_url_rule(
        '/session/workers',   # TODO: split into training and testing
        methods=['GET'],
        view_func=SessionWorkers.as_view('active_workers', session_executor)
    )

    app.add_url_rule(
        '/session/start',  # TODO: split into training and testing
        methods=['POST'],
        view_func=SessionStart.as_view('session_start', session_executor)
    )

    app.add_url_rule(
        '/session',  # TODO: split into training and testing
        methods=['DELETE'],
        view_func=SessionCancel.as_view('session_delete', session_executor)
    )

    app.add_url_rule(
        '/session/list', # TODO: split into training and testing
        methods=['GET'],
        view_func=ActiveSessions.as_view('active_sessions', session_executor)
    )

    app.add_url_rule(
        '/session/proxy', 
        methods=['POST'],
        view_func=SessionProxy.as_view('session_proxy', session_executor)
    )

    app.add_url_rule(
        '/serving/start',
        methods=['POST'], 
        view_func=ServingStart.as_view('serving_start', session_executor)
    )

    app.add_url_rule(
        '/serving/model',  # TODO. use the serving/models/<id> endpoint instead
        methods=['GET'],
        view_func=IsServedModelReady.as_view('is_served_model_ready', session_executor)
    )

    models_view = Models.as_view('models', session_executor)
    app.add_url_rule(
        '/serving/models', methods=['GET'], view_func=models_view, defaults={'model_id': None})
    app.add_url_rule(
        '/serving/models/<model_id>', methods=['GET'], view_func=models_view)

    app.add_url_rule(
        '/export',
        methods=['POST'],
        view_func=Export.as_view('export', model_access, epochs_access, data_metadata_cache=data_metadata_cache)
    )

    @app.route('/healthy', methods=['GET'])
    def healthy():
        return '{"healthy": "true"}'


    @app.route('/has_checkpoint', methods=['GET'])
    def has_checkpoint():
        checkpoint_directory = request.args.get('directory')  # TODO: frontend should send ID

        has_checkpoint = epochs_access.has_saved_epoch(
            checkpoint_directory, require_trainer_state=False)
        
        return jsonify(has_checkpoint)


    @app.before_request
    def before_request():
        g.request_started = time.perf_counter()


    @app.after_request
    def after_request(response):
        duration = time.perf_counter() - g.request_started

        if request.endpoint == 'session_proxy':
            action = (request.get_json() or {}).get('action')
            logger.info(
                f"Request to endpoint '{request.endpoint}' took {duration:.4f}s. Action: '{action}'")
        else:
            logger.info(f"Request to endpoint '{request.endpoint}' took {duration:.4f}s")
            
        return response

    @app.errorhandler(Exception)
    def handle_endpoint_error(e):
        message = traceback_from_exception(e)
        print(message)
        logger.exception(f"Error in request '{request.endpoint}'")
        return make_response(message), 500

    return app
