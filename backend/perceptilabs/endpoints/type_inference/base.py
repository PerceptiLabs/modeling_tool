from flask import request, jsonify
from flask.views import View

import perceptilabs.tracking as tracking
from perceptilabs.data.type_inference import TypeInferrer
from perceptilabs.utils import KernelError

class TypeInference(View):
    def __init__(self, dataset_access):
        self._dataset_access = dataset_access
    
    def dispatch_request(self):
        """ Sent when the users selects a data file """        
        inferrer = TypeInferrer(
            always_allowed=['categorical'],
            never_allowed=['binary']
        )
        try:
            datatypes = inferrer.get_valid_and_default_datatypes_for_csv(request.args['path'])
        except ValueError as e:
            raise KernelError.from_exception(
                e, message="Couldn't get data types because the Kernel responded with an error")
        else:
            if 'user_email' in request.args:
                is_plabs_sourced = self._dataset_access.is_perceptilabs_sourced(
                    request.args['dataset_id'])
            
                tracking.send_data_selected(
                    request.args['user_email'],
                    request.args['path'],
                    is_plabs_sourced,
                    request.args['dataset_id']                    
                )
            return jsonify(datatypes)
