import time
import logging

from flask_cors import CORS
from flask_compress import Compress
from flask import Flask, request, g, jsonify, abort, make_response, json
from flask.json import JSONEncoder
from werkzeug.exceptions import HTTPException
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from perceptilabs.caching.utils import get_preview_cache, get_data_metadata_cache, NullCache
from perceptilabs.messaging.base import get_message_broker
from perceptilabs.tasks.utils import get_task_executor
from perceptilabs.resources.training_results import TrainingResultsAccess
from perceptilabs.resources.testing_results import TestingResultsAccess
from perceptilabs.resources.serving_results import ServingResultsAccess
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.endpoints.version.base import Version
from perceptilabs.endpoints.network_data.base import NetworkData, Previews
from perceptilabs.endpoints.data.base import PutData, IsDataReady
from perceptilabs.endpoints.model_recommendations.base import ModelRecommendations
from perceptilabs.endpoints.type_inference.base import TypeInference
from perceptilabs.endpoints.layer_code.base import LayerCode
from perceptilabs.endpoints.set_user.base import SetUser
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.issues import traceback_from_exception
from perceptilabs.models.api import create_blueprint as create_models_blueprint
import perceptilabs.utils as utils


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

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        return utils.convert(obj)

    
def create_app(
        data_metadata_cache = NullCache(),
        preview_cache = NullCache(),
        data_executor = utils.DummyExecutor(),
        task_executor = get_task_executor(),
        message_broker = get_message_broker(),            
        models_access = ModelAccess(),        
        epochs_access = EpochsAccess(),
        training_results_access = TrainingResultsAccess(),
        testing_results_access = TestingResultsAccess(),
        serving_results_access = ServingResultsAccess()                        
):
    app = Flask(__name__)
    app.json_encoder = MyJSONEncoder

    CORS(app, resources={r'/*': {'origins': '*'}})
    
    compress = Compress()
    compress.init_app(app)

    models = create_models_blueprint(
        task_executor,
        message_broker,
        models_access,
        epochs_access,
        training_results_access,
        testing_results_access,
        serving_results_access,                
        data_metadata_cache        
    )
    app.register_blueprint(models)

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
            models_access,
            data_metadata_cache=data_metadata_cache, preview_cache=preview_cache
        )
    )

    previews_view = Previews.as_view(
        'previews',
        models_access,
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
        view_func=LayerCode.as_view('layer_code', models_access)
    )

    @app.route('/healthy', methods=['GET'])
    def healthy():
        return '{"healthy": "true"}'

    @app.before_request
    def before_request():
        g.request_started = time.perf_counter()


    @app.after_request
    def after_request(response):
        duration = time.perf_counter() - g.request_started
        logger.info(f"Request to endpoint '{request.endpoint}' took {duration:.4f}s")
        return response

    @app.errorhandler(Exception)
    def handle_endpoint_error(error):
        # TODO: Sentry capture here???? probably on original exception...
        logger.exception(f"Error in request '{request.url}'")
        
        if not isinstance(error, utils.KernelError):
            error = utils.KernelError.from_exception(error)
            
        return jsonify({"error": error.to_dict()}), 200   
            
    #print(app.url_map)
    return app


