from mixpanel import Mixpanel
import os
import logging
import datetime
import functools

from perceptilabs.mixpanel_handler import MIXPANEL_TOKEN_DEV, MIXPANEL_TOKEN_PROD
from perceptilabs.utils import is_dev
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

_DEFAULT_TOKEN = MIXPANEL_TOKEN_DEV if is_dev() else MIXPANEL_TOKEN_PROD
_TOKEN = os.getenv("PL_MIXPANEL_TOKEN", _DEFAULT_TOKEN)
_MIXPANEL = Mixpanel(_TOKEN)


def get_mixpanel(user_email):
    current_time = datetime.datetime.utcnow()
    _MIXPANEL.people_set_once(user_email, {'$created': current_time})    
    _MIXPANEL.people_set(user_email, {'$email': user_email, '$last_login': current_time})    
    return _MIXPANEL


def silence_exceptions(function):
    @functools.wraps(function)
    def func(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            if is_dev:
                logger.exception("Tracker crashed")
    return func
