import time
import logging
import sys

from flask_cors import CORS
from flask_compress import Compress
from flask import Flask, request, g, jsonify, abort, make_response, json
from flask.json import JSONEncoder
from werkzeug.exceptions import HTTPException
import tensorflow as tf
import sentry_sdk

from perceptilabs.caching.utils import get_preview_cache, get_data_metadata_cache, NullCache, DictCache
from perceptilabs.messaging.base import get_message_broker
from perceptilabs.tasks.utils import get_task_executor
from perceptilabs.datasets_interface import DatasetsInterface
from perceptilabs.models_interface import ModelsInterface
from perceptilabs.inference_interface import InferenceInterface
from perceptilabs.resources.training_results import TrainingResultsAccess
from perceptilabs.resources.testing_results import TestingResultsAccess
from perceptilabs.resources.datasets import DatasetAccess
from perceptilabs.resources.serving_results import ServingResultsAccess
from perceptilabs.resources.preprocessing_results import PreprocessingResultsAccess
from perceptilabs.resources.models import ModelAccess
from perceptilabs.resources.model_archives import ModelArchivesAccess
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.issues import traceback_from_exception
from perceptilabs.rygg import RyggWrapper
from perceptilabs import __version__
from perceptilabs.tracking.base import EventTracker
import perceptilabs.utils as utils
import perceptilabs.tracking as tracking



logger = logging.getLogger(__name__)


rygg = RyggWrapper.with_default_settings()


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        return utils.convert(obj)


def maybe_get_email(request):
    email = None
    if 'Authorization' in request.headers:
        email = utils.parse_user_email(request.headers['Authorization'])
    return email

    
def create_app(
        preview_cache=None,
        task_executor=None,
        message_broker=None,
        event_tracker=None,
        models_access=None,
        model_archives_access=None,
        epochs_access=None,
        dataset_access=None,
        training_results_access=None,
        testing_results_access=None,
        serving_results_access=None,
        preprocessing_results_access=None,
):
    # Defer creating objects until function is actually called to ensure any mocking happens first
    preview_cache = preview_cache or NullCache()
    task_executor = task_executor or get_task_executor()
    message_broker = message_broker or get_message_broker()
    event_tracker = event_tracker or EventTracker()       
    models_access = models_access or ModelAccess()
    model_archives_access = model_archives_access or ModelArchivesAccess()
    epochs_access = epochs_access or EpochsAccess()
    dataset_access = dataset_access or DatasetAccess(rygg)
    training_results_access = training_results_access or TrainingResultsAccess()
    testing_results_access = testing_results_access or TestingResultsAccess()
    serving_results_access = serving_results_access or ServingResultsAccess()
    preprocessing_results_access = preprocessing_results_access or PreprocessingResultsAccess(get_data_metadata_cache())

    
    app = Flask(__name__)
    app.json_encoder = MyJSONEncoder

    CORS(app, resources={r'/*': {'origins': '*'}})
    
    compress = Compress()
    compress.init_app(app)

    datasets_interface = DatasetsInterface(
        task_executor, event_tracker, preprocessing_results_access, dataset_access)

    models_interface = ModelsInterface(
        task_executor,
        message_broker,
        event_tracker,
        dataset_access,
        models_access,
        model_archives_access,
        epochs_access,
        training_results_access,
        preprocessing_results_access,
        preview_cache
    )

    inference_interface = InferenceInterface(
        task_executor,
        message_broker,
        testing_results_access,
        serving_results_access
    )

    @app.route('/user', methods=['POST'])
    def set_user():
        json_data = request.get_json()
        user_email = maybe_get_email(request)

        tracking.send_user_email_set(event_tracker, user_email)
            
        logger.info("User has been set to %s" % str(user_email))
        return jsonify(f"User has been set to {user_email}")


    @app.route('/version', methods=['GET'])
    def get_version():
        content = {
            "python": sys.version,
            "tensorflow": tf.__version__,
            "perceptilabs": __version__
        }
        return jsonify(content)        
    
    @app.route('/datasets/preprocessing', methods=['PUT'])
    def put_preprocessing():
        json_data = request.get_json()
        settings_dict = json_data['datasetSettings']
        user_email = json_data.get('userEmail')
        logrocket_url = request.headers.get('X-LogRocket-URL', '') 

        session_id = datasets_interface.start_preprocessing(
            settings_dict, user_email, logrocket_url=logrocket_url)

        return jsonify({"preprocessingSessionId": session_id})

    
    @app.route('/datasets/preprocessing/<preprocessing_session_id>', methods=['GET'])
    def get_preprocessing(preprocessing_session_id):
        message, is_present, is_complete, error = datasets_interface.get_preprocessing_status(
            preprocessing_session_id)

        if is_present:
            response = {
                'message': f"Build status: '{message}'",
                'is_complete': is_complete,
                'error': error
            }
        
            return jsonify(response)
        else:
            return make_response('', 204)
        

    @app.route('/models/recommendations', methods=['POST'])
    def get_model_recommendation():
        json_data = request.get_json()        
        graph_spec_dict = models_interface.get_model_recommendation(
            json_data.get('modelId'),
            json_data.get('skippedWorkspace'),
            json_data['datasetSettings'],
            user_email=maybe_get_email(request)
        )
        return jsonify(graph_spec_dict)

    @app.route('/models/import', methods=['POST'])    
    def import_model():
        json_data = request.get_json()
        
        output = models_interface.import_model(
            json_data["datasetId"],
            json_data["modelFilePath"]
        )
        return jsonify(output)
    

    @app.route('/models/<model_id>/layers/<layer_id>/code', methods=['POST'])
    def get_layer_code(model_id, layer_id):
        json_data = request.get_json()
        return models_interface.get_layer_code(model_id, layer_id, json_data['network'])

    @app.route('/models/<model_id>/layers/previews', methods=['POST'])
    def get_previews(model_id):
        json_data = request.get_json()
        content = models_interface.get_previews(
            model_id,
            dataset_settings_dict=json_data['datasetSettings'],
            graph_spec_dict=json_data['network'],
            user_email=json_data.get('userEmail')
        )
        return jsonify(content)
    
    @app.route('/models/<model_id>/layers/info', methods=['POST'])
    @app.route('/models/<model_id>/layers/<layer_id>/info', methods=['POST'])
    def get_layer_info(model_id, layer_id=None):
        json_data = request.get_json()
        content = models_interface.get_layer_info(
            model_id,
            dataset_settings_dict=json_data['datasetSettings'],
            graph_spec_dict=json_data['network'],
            user_email=json_data.get('userEmail'),
            layer_id=layer_id
        )
        return jsonify(content)

    @app.route('/datasets/type_inference', methods=['GET'])
    def type_inference():
        datatypes = datasets_interface.infer_datatypes(
            request.args['dataset_id'],
            user_email=maybe_get_email(request)            
        )        
        return jsonify(datatypes)
    
    @app.route('/healthy', methods=['GET'])
    def healthy():
        return '{"healthy": "true"}'


    @app.route('/models/<model_id>/training/<training_session_id>', methods=['POST'])
    def start_training(model_id, training_session_id):
        json_data = request.get_json()
        graph_spec_dict = json_data['network']
        dataset_settings = json_data['datasetSettings']
        training_settings = json_data['trainingSettings']
        load_checkpoint = json_data['loadCheckpoint']
        logrocket_url = request.headers.get('X-LogRocket-URL', '')         

        models_interface.start_training(
            dataset_settings,
            model_id,
            graph_spec_dict,
            training_session_id,
            training_settings,
            load_checkpoint,
            maybe_get_email(request),            
            logrocket_url=logrocket_url            
        )
        return jsonify({"content": "core started"})

    @app.route('/models/<model_id>/training/<training_session_id>/stop', methods=['PUT'])
    def stop_training(model_id, training_session_id):
        models_interface.stop_training(model_id, training_session_id)        
        return jsonify('success')

    @app.route('/models/<model_id>/training/<training_session_id>/pause', methods=['PUT'])
    def pause_training(model_id, training_session_id):
        models_interface.pause_training(model_id, training_session_id)
        return jsonify('success')

    @app.route('/models/<model_id>/training/<training_session_id>/unpause', methods=['PUT'])
    def unpause_training(model_id, training_session_id):
        models_interface.unpause_training(model_id, training_session_id)
        return jsonify('success')

    @app.route('/models/<model_id>/training/<training_session_id>/has_checkpoint', methods=['GET'])
    def has_checkpoint(model_id, training_session_id):
        has_checkpoint = models_interface.has_checkpoint(model_id, training_session_id)        
        return jsonify(has_checkpoint)

    @app.route('/models/<model_id>/training/<training_session_id>/status', methods=['GET'])
    def training_status(model_id, training_session_id):
        output = models_interface.get_training_status(model_id, training_session_id)        
        return jsonify(output)
    
    @app.route('/models/<model_id>/training/<training_session_id>/results', methods=['GET'])
    def training_results(model_id, training_session_id):
        output = models_interface.get_training_results(
            model_id, training_session_id, request.args.get('type'),
            layer_id=request.args.get('layerId'), view=request.args.get('view'))
        return jsonify(output)

    @app.route('/models/<model_id>/export', methods=['PUT'])
    def export(model_id):
        json_data = request.get_json()
        training_session_id = request.args.get('training_session_id')        
        graph_spec_dict = json_data['network']
        dataset_settings_dict = json_data['datasetSettings']
        export_options = json_data['exportSettings']        
        user_email = maybe_get_email(request)        
        training_settings = json_data.get('trainingSettings')        
        frontend_settings = json_data.get('frontendSettings')

        status = models_interface.export(
            export_options,
            model_id,
            graph_spec_dict,
            dataset_settings_dict,
            training_session_id,
            user_email,
            training_settings,
            frontend_settings
        )        
        return jsonify(status)

    @app.route('/inference/serving/<model_id>', methods=['POST'])
    def start_serving(model_id):
        json_data = request.get_json()
        session_id = inference_interface.start_serving(
            json_data['settings'],
            json_data['datasetSettings'],
            json_data['network'],
            model_id,
            request.args.get('training_session_id'),            
            json_data['modelName'],
            maybe_get_email(request),                    
            logrocket_url=request.headers.get('X-LogRocket-URL', '')         
        )        
        return jsonify(session_id)

    @app.route('/inference/serving/<serving_session_id>/status', methods=['GET'])
    def serving_status(serving_session_id):
        output = inference_interface.get_serving_status(serving_session_id)
        return jsonify(output)

    @app.route('/inference/serving/<serving_session_id>/stop', methods=['POST'])
    def stop_serving(serving_session_id):
        inference_interface.stop_serving(serving_session_id)        
        return jsonify('success')
    
    @app.route('/inference/testing', methods=['POST'])
    def start_testing():
        json_data = request.get_json()
        models_info = json_data['modelsInfo']
        tests = json_data['tests']        
        user_email = maybe_get_email(request)
        logrocket_url = request.headers.get('X-LogRocket-URL', '')         

        session_id = inference_interface.start_testing(
            models_info, tests, user_email, logrocket_url=logrocket_url)
        return jsonify(session_id)

    @app.route('/inference/testing/<testing_session_id>/status', methods=['GET'])
    def testing_status(testing_session_id):
        output = inference_interface.get_testing_status(testing_session_id)
        return jsonify(output)
    
    @app.route('/inference/testing/<testing_session_id>/results', methods=['GET'])
    def testing_results(testing_session_id):
        output = inference_interface.get_testing_results(testing_session_id)
        return jsonify(output)


    @app.before_request
    def before_request():
        g.request_started = time.perf_counter()


    @app.after_request
    def after_request(response):
        duration = time.perf_counter() - g.request_started
        logger.info(f"Request to endpoint '{request.endpoint}' took {duration:.4f}s")
        return response

    @app.errorhandler(Exception)
    def handle_endpoint_error(original_error):        
        logger.exception(f"Error in request '{request.url}'")
        
        if not isinstance(original_error, utils.KernelError):
            error = utils.KernelError.from_exception(original_error)
        else:
            error = original_error

        response = {"error": error.to_dict()}

        email = maybe_get_email(request)        
        
        with sentry_sdk.push_scope() as scope:
            scope.set_user({'email': email})
            scope.set_extra('url', request.url)            
            scope.set_extra('request', request.json)
            scope.set_extra('response', response)
            scope.set_extra('logrocket-url', request.headers.get('X-LogRocket-URL', ''))
            sentry_sdk.capture_exception(original_error)
            
        return jsonify(response), 200   
            
    #print(app.url_map)
    return app


