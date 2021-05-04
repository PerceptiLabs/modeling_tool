from perceptilabs.tracking.base import get_mixpanel, silence_exceptions
from perceptilabs.tracking.utils import get_layer_counts


@silence_exceptions
def send_testing_completed(user_email, model_id, test_name):
    payload = {
        'user_email': user_email,
        'model_id': model_id,
        'test_name': test_name
    }
    mp = get_mixpanel(user_email)
    mp.track(user_email, 'testing-completed', payload)

