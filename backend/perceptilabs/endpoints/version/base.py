from flask import jsonify
from flask.views import View
from perceptilabs import __version__

import tensorflow as tf
import sys


class Version(View):
    def dispatch_request(self):
        """ Request endpoint for getting PL version, Python version, and TensorFlow version. """        
        return jsonify({"python": sys.version,
                        "tensorflow": tf.__version__,
                        "perceptilabs": __version__})
