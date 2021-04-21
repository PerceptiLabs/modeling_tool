from mixpanel import Mixpanel
import os
import datetime
import functools
from perceptilabs.mixpanel_handler import MIXPANEL_TOKEN_DEV

TOKEN = os.getenv("PL_MIXPANEL_TOKEN", MIXPANEL_TOKEN_DEV)
_MIXPANEL = Mixpanel(TOKEN)


def get_mixpanel(user_email):
    if not TOKEN:
        return None
        
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
            pass
    return func
