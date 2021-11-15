import time
import logging
import sys

from flask_cors import CORS
from flask_compress import Compress
from flask import Flask, request, g, jsonify, abort, make_response, json
from flask.json import JSONEncoder
from werkzeug.exceptions import HTTPException
import tensorflow as tf

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
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.script import ScriptFactory
from perceptilabs.issues import traceback_from_exception
from perceptilabs import __version__
import perceptilabs.utils as utils
import perceptilabs.tracking as tracking


logger = logging.getLogger(__name__)



class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        return utils.convert(obj)

    
def create_app(
        preview_cache = NullCache(),
        task_executor = get_task_executor(),
        message_broker = get_message_broker(),            
        models_access = ModelAccess(),        
        epochs_access = EpochsAccess(),
        dataset_access = DatasetAccess(),
        training_results_access = TrainingResultsAccess(),
        testing_results_access = TestingResultsAccess(),
        serving_results_access = ServingResultsAccess(),
        preprocessing_results_access = PreprocessingResultsAccess(get_data_metadata_cache())
):
    app = Flask(__name__)
    app.json_encoder = MyJSONEncoder

    CORS(app, resources={r'/*': {'origins': '*'}})
    
    compress = Compress()
    compress.init_app(app)

    datasets_interface = DatasetsInterface(
        task_executor, preprocessing_results_access, dataset_access)

    models_interface = ModelsInterface(
        task_executor,
        message_broker,
        dataset_access,
        models_access,
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
        user_email = json_data["userEmail"]

        if not utils.is_pytest():
            tracking.send_user_email_set(user_email)
            
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

        session_id = datasets_interface.start_preprocessing(
            settings_dict, user_email)

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
            json_data.get('userEmail')
        )
        return jsonify(graph_spec_dict)
        
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
            request.args['path'],
            request.args.get('dataset_id'),
            user_email=request.args.get('user_email')
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
        user_email = json_data['userEmail']                                        

        models_interface.start_training(
            dataset_settings,
            model_id,
            graph_spec_dict,
            training_session_id,
            training_settings,
            load_checkpoint,
            user_email
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
        user_email = json_data.get('userEmail')

        status = models_interface.export(
            export_options,
            model_id,
            graph_spec_dict,
            dataset_settings_dict,
            training_session_id,
            user_email
        )        
        return jsonify(status)

    @app.route('/inference/serving/<model_id>', methods=['POST'])
    def start_serving(model_id):
        json_data = request.get_json()

        session_id = inference_interface.start_serving(
            json_data['type'],
            json_data['datasetSettings'],
            json_data['network'],
            model_id,
            request.args.get('training_session_id'),            
            json_data['modelName'],
            json_data['userEmail']
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
        user_email = json_data.get('userEmail')

        session_id = inference_interface.start_testing(models_info, tests, user_email)
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
    def handle_endpoint_error(error):
        # TODO: Sentry capture here???? probably on original exception...
        logger.exception(f"Error in request '{request.url}'")
        
        if not isinstance(error, utils.KernelError):
            error = utils.KernelError.from_exception(error)
            
        return jsonify({"error": error.to_dict()}), 200   
            
    #print(app.url_map)
    return app


