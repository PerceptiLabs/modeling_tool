""" WARNING: this module contains a temporary workaround needed for the September 2020 release and will be deprecated soon. Speak with Craig or Anton before making changes """
import json
import logging
import datetime

from mixpanel import Mixpanel

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


MIXPANEL_TOKEN_PROD = '1480b2244fdd4d821227a29e2637f922'
MIXPANEL_TOKEN_DEV = '8312db76002e43f8a9dc9acf9a12c1fc'


mp = Mixpanel(MIXPANEL_TOKEN_PROD)


def event_common(event_full):
    payload = {
        '$email': event_full['user_email'],
        '$time': event_full['time_event'],
        'Session ID': event_full['session_id'],
        'Version': event_full['version'],
        'Commit': event_full['commit']
    }

    system = event_full.get('system')
    mixpanel_os = {'Darwin': 'Mac OS X', 'Linux': 'Linux', 'Windows': 'Windows'}
    if system in mixpanel_os:
        payload['OS'] = mixpanel_os[system]
    
    return payload


def event_user_email_set(event_full, event_namespace):
    payload = event_common(event_full)
    payload['Number of GPUs'] = len(event_namespace['gpus'])
    payload['Number of CPUs'] = event_namespace['cpu_count']
    return payload


def event_training_started(event_full, event_namespace):
    payload = event_common(event_full)
    payload['Training Session ID'] = event_namespace.get('training_session_id', '')    
    payload['Model ID'] = event_namespace['model_id']
    payload['Number of components'] = len(event_namespace['graph_spec']['nodes'])
    
    payload['Has train classification'] = False
    payload['Has train objectdetection'] = False
    payload['Has train regression'] = False
    payload['Has train GAN'] = False
    payload['Has train RL'] = False       

    payload['Has DataData'] = False
    payload['Has DataEnv'] = False
    payload['Has DataRandom'] = False

    payload['Number of csv files'] = 0
    payload['Number of npy/npz files'] = 0
    payload['Number of txt files'] = 0
    payload['Number of jpg/jpeg/png/tif/tiff files'] = 0
    payload['Number of other files'] = 0        

    for node in event_namespace['graph_spec']['nodes']:
        type_ = node['type']

        if type_ == 'TrainNormal':
            payload['Has train classification'] = True
        elif type_ == 'TrainDetector':
            payload['Has train objectdetection'] = True
        elif type_ == 'TrainRegression':            
            payload['Has train regression'] = True
        elif type_ == 'TrainGan':            
            payload['Has train GAN'] = True
        elif type_ == 'TrainReinforce':            
            payload['Has train RL'] = True
        elif type_ == 'DataData':            
            payload['Has DataData'] = True
            
            for ext in node['namespace']['extensions']:
                if ext == '.csv':
                    payload['Number of csv files'] += 1
                elif ext in ['.npy', '.npz']:
                    payload['Number of npy/npz files'] += 1
                elif ext == '.txt':
                    payload['Number of txt files'] += 1
                elif ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                    payload['Number of jpg/jpeg/png/tif/tiff files'] += 1
                else:
                    payload['Number of other files'] += 1
                    
        elif type_ == 'DataEnvironment':            
            payload['Has data environment'] = True
        elif type_ == 'DataRandom':            
            payload['Has DataRandom'] = True
            
    return payload


def event_training_ended(event_full, event_namespace):
    payload = event_training_started(event_full, event_namespace)

    payload['Training time'] = event_namespace['time_total']
    payload['End state'] = event_namespace.get('end_state', 'not-available')


    if any('sample_shape' in dm for dm in event_namespace['data_meta']):
        payload['Number of 0D shapes'] = 0
        payload['Number of 1D shapes'] = 0
        payload['Number of 2D shapes'] = 0
        payload['Number of 3D shapes'] = 0    
        payload['Number of other shapes'] = 0        
        
        for data_meta in event_namespace['data_meta']:
            dim = len(data_meta['sample_shape'])

            payload['Number of 0D shapes'] += int(dim == 0)
            payload['Number of 1D shapes'] += int(dim == 1)
            payload['Number of 2D shapes'] += int(dim == 2)
            payload['Number of 3D shapes'] += int(dim == 3)
            payload['Number of other shapes'] += int(dim > 3)
        
    return payload


event_handlers = {
    'user_email_set': event_user_email_set,
    'training_started': event_training_started,
    'training_ended': event_training_ended
}


class MixPanelHandler(logging.Handler):
    def emit(self, record):
        #if self._producer is not None:
        message = self.format(record)

        try:
            event_original = json.loads(message)
        except:
            logger.debug("Failed loading json from message: " + message)
        else:
            self._transform_and_track(event_original)

    def _transform_and_track(self, event_original):
        try:
            user_id = event_original['user_email']
        except:
            logger.debug("Failed getting user from event ")
            return

        current_time = datetime.datetime.utcnow()
        try:
            mp.people_set_once(user_id, {'$created': current_time})
            mp.people_set(
                user_id,
                {'$email': event_original['user_email'], '$last_login': current_time}
            )
        except:
            logger.debug("Failed setting mixpanel user")
            return
        
        for event_id, event_handler in event_handlers.items():
            if event_id in event_original: # One or more event_ids exist at the top level, serving as a namespace for that event
                logger.debug("Found event: " + event_id)
                
                try:
                    event_transformed = event_handler(event_original, event_original[event_id])
                    logger.debug("Transformed event: " + event_id)
                except:
                    logger.debug("Failed transforming event " + event_id)
                else:
                    # Disabling the tracking for now.
                    mp.track(user_id, event_id, event_transformed) 
                    logger.debug("Tracked event: " + event_id)


