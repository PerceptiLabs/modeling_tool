from flask import request, jsonify
from flask.views import View

import perceptilabs.tracking as tracking
from perceptilabs.data.type_inference import TypeInferrer


class TypeInference(View):
    def dispatch_request(self):
        """ Sent when the users selects a data file """        
        inferrer = TypeInferrer(always_allow_categorical=True)
        datatypes = inferrer.get_valid_and_default_datatypes_for_csv(request.args['path'])

        if 'user_email' in request.args:
            tracking.send_data_selected(
                request.args['user_email'],
                request.args['path']
            )        
        return jsonify(datatypes)
