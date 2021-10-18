from flask import request, jsonify
from flask.views import View

from perceptilabs.stats.base import OutputStats


class TrainingStatus(View):
    def __init__(self, results_access):
        self._results_access = results_access
    
    def dispatch_request(self, model_id, training_session_id):
        results_dict = self._results_access.get_latest(training_session_id)
        if not results_dict:
            return jsonify({})            

        result = {
            "Status": results_dict["trainingStatus"],
            "Iterations": results_dict["iter"],
            "Epoch": results_dict["epoch"],
            "Progress": results_dict["progress"],
            "CPU": results_dict["cpu_usage"],
            "GPU": results_dict["gpu_usage"],
            "Memory": results_dict["mem_usage"],
            "Training_Duration": results_dict["training_duration"],
        }
        return jsonify(result)        



class TrainingResults(View):
    def __init__(self, results_access):
        self._results_access = results_access
    
    def dispatch_request(self, model_id, training_session_id):
        type_ = request.args.get('type')

        results_dict = self._results_access.get_latest(training_session_id)
        if not results_dict:
            return jsonify({})

        if type_ == 'global-results':
            output = self._get_global_results(results_dict)            
        elif type_ == 'end-results':
            output = self._get_end_results(results_dict)
        elif type_ == 'layer-results':
            output = self._get_layer_results(
                results_dict, request.args['layerId'], request.args.get('view'))
        else:
            output = {
                'global_results': self._get_global_results(results_dict),
                'end_results': self._get_end_results(results_dict),
                'layer_results': self._get_layer_results(
                    results_dict, request.args['layerId'], request.args.get('view'))
            }            
            
        return jsonify(output)

    def _get_global_results(self, results_dict):
        stats = results_dict['global_stats']
        output = stats.get_data_objects()
        return output

    def _get_end_results(self, results_dict):
        global_stats = results_dict['global_stats']
        
        end_results = {}        
        end_results['global_stats'] = global_stats.get_end_results()
        
        #layer specific stats

        for layer_id, obj in results_dict['layer_stats'].items():
            if isinstance(obj, OutputStats):  # OutputStats are guaranteed to have end results
                end_results[layer_id] = obj.get_end_results()
                
        return end_results
        
    def _get_layer_results(self, results_dict, layer_id, view):
        stats = results_dict['layer_stats'][layer_id]        
        output = stats.get_data_objects(view=view)
        return output

