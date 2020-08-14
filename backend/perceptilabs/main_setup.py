import os

import logging
import sentry_sdk
from sentry_sdk import utils

import perceptilabs.utils as utils
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

def setup_sentry(user=None, commit_id=None):
    def strip_unimportant_errors(event, hint):
        log_ignores=['Error in getTestingStatistics', 'Error in getTrainingStatistics', ]

        if 'log_record' in hint:
            if hint['log_record'].msg in log_ignores:
                return None

        return event

    sentry_sdk.init("https://9b884d2181284443b90c21db68add4d7@sentry.io/1512385", before_send=strip_unimportant_errors, release=str(commit_id))

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag('error-type', 'internal-error')
        sentry_sdk.utils.MAX_STRING_LENGTH = 8192

        if user:
            scope.user = {"email" : user}
