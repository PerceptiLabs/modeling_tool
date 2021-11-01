from flask import request, jsonify, Blueprint
from flask.views import View
from flask_cors import CORS

from perceptilabs.models.interface import ModelsInterface
import perceptilabs.utils as utils


def create_blueprint(
        task_executor, message_broker,
        models_access, epochs_access,
        training_results_access, testing_results_access,
        data_metadata_cache        
):    
    models_interface = ModelsInterface(
        task_executor,
        message_broker,
        models_access,
        epochs_access,
        training_results_access,
        testing_results_access,        
        data_metadata_cache
    )
    
    bp = Blueprint('models', __name__)
    CORS(bp, resources={r'/*': {'origins': '*'}})    
    
    @bp.route('/models/<model_id>/training/<training_session_id>', methods=['POST'])
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

    @bp.route('/models/<model_id>/training/<training_session_id>/stop', methods=['PUT'])
    def stop_training(model_id, training_session_id):
        models_interface.stop_training(model_id, training_session_id)        
        return jsonify('success')

    @bp.route('/models/<model_id>/training/<training_session_id>/pause', methods=['PUT'])
    def pause_training(model_id, training_session_id):
        models_interface.pause_training(model_id, training_session_id)
        return jsonify('success')

    @bp.route('/models/<model_id>/training/<training_session_id>/unpause', methods=['PUT'])
    def unpause_training(model_id, training_session_id):
        models_interface.unpause_training(model_id, training_session_id)
        return jsonify('success')

    @bp.route('/models/<model_id>/training/<training_session_id>/has_checkpoint', methods=['GET'])
    def has_checkpoint(model_id, training_session_id):
        has_checkpoint = models_interface.has_checkpoint(model_id, training_session_id)        
        return jsonify(has_checkpoint)

    @bp.route('/models/<model_id>/training/<training_session_id>/status', methods=['GET'])
    def training_status(model_id, training_session_id):
        output = models_interface.get_training_status(model_id, training_session_id)        
        return jsonify(output)
    
    @bp.route('/models/<model_id>/training/<training_session_id>/results', methods=['GET'])
    def training_results(model_id, training_session_id):
        output = models_interface.get_training_results(
            model_id, training_session_id, request.args.get('type'),
            layer_id=request.args.get('layerId'), view=request.args.get('view'))
        return jsonify(output)

    @bp.route('/models/<model_id>/training/<training_session_id>/export', methods=['POST'])
    def export(model_id, training_session_id):
        json_data = request.get_json()
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

    @bp.route('/models/testing', methods=['POST'])
    def start_testing():
        json_data = request.get_json()
        models_info = json_data['modelsInfo']
        tests = json_data['tests']        
        user_email = json_data.get('userEmail')

        session_id = models_interface.start_testing(models_info, tests, user_email)
        return jsonify(session_id)

    @bp.route('/models/testing/<testing_session_id>/status', methods=['GET'])
    def testing_status(testing_session_id):
        output = models_interface.get_testing_status(testing_session_id)
        return jsonify(output)
    
    @bp.route('/models/testing/<testing_session_id>/results', methods=['GET'])
    def testing_results(testing_session_id):
        output = models_interface.get_testing_results(testing_session_id)
        return jsonify(output)

    return bp
