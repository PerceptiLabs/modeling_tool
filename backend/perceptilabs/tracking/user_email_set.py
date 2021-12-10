import datetime

from perceptilabs.tracking.utils import get_tool_version, get_system, get_cpu_count, get_gpu_count


def send_user_email_set(tracker, user_email):
    """ Sends a MixPanel event when user logs in """

    payload = {
        'email': user_email,
        'Version': get_tool_version(),
        '$time': datetime.datetime.utcnow().isoformat(),
        'Session ID': '',  # TODO: was never implemented. 
        'Number of GPUs': get_gpu_count(),
        'Number of CPUs': get_cpu_count(),
        'OS': get_system()
    }
    tracker.emit('user_email_set', user_email, payload)     
