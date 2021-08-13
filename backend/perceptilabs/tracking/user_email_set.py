import datetime

from perceptilabs.logconf import _global_context
from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_tool_version, get_system, get_cpu_count, get_gpu_count


@silence_exceptions
def send_user_email_set(user_email):
    """ Sends a MixPanel event when user logs in """

    payload = {
        'email': user_email,
        'Version': get_tool_version(),
        '$time': datetime.datetime.utcnow().isoformat(),
        'Session ID': _global_context.get('session_id', ''),
        'Number of GPUs': get_gpu_count(),
        'Number of CPUs': get_cpu_count(),
        'OS': get_system()
    }
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'user_email_set', payload)


