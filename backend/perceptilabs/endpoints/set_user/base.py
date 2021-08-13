from flask import request, jsonify
from flask.views import View
import logging

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.tracking as tracking

logger = logging.getLogger(APPLICATION_LOGGER)

class SetUser(View):

    def dispatch_request(self):
        """ Renders the code for a layer """
        json_data = request.get_json()
        user_email = json_data["userEmail"]
        tracking.send_user_email_set(user_email)
        logger.info("User has been set to %s" % str(user_email))
        return jsonify(f"User has been set to {user_email}")
