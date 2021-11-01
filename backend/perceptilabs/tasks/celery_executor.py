# TODO: update celery module path in Docker
import logging
from celery import Celery, shared_task


import perceptilabs.settings as settings
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.tasks.base import (
    TaskExecutor,
    training_task
)


logger = logging.getLogger(APPLICATION_LOGGER)


CELERY_APP = Celery(
    'training',
    backend=settings.CELERY_REDIS_URL,
    broker=settings.CELERY_REDIS_URL,
    imports=('perceptilabs',),
    task_routes={
        'session_task': {
            'queue': 'training'
        },
        'training_task': {
            'queue': 'training'
        }        
    }
)

@shared_task(
    bind=True,
    name="session_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def session_task(self, session_type, start_payload):
    
    def on_task_started(start_payload, port):
        meta = {
            'hostname': self.request.hostname,
            'port': port,
            'payload': start_payload,
            'type': session_type
        }
        
        self.update_state(
            state='STARTED',
            meta=meta,
        )

    # TODO: start a thread that polls for cancelation
    # when detected, trigger the cancel_token

    logger.info(f"Received session_task for session type: '{session_type}'")

    import perceptilabs.session.utils as session_utils
    session_class = session_utils.DEFAULT_SESSION_CLASSES.get(session_type)
    if session_class:
        session = session_class()

        try:
            session.start(
                start_payload,
                is_retry=(self.request.retries > 0),        
                on_task_started=on_task_started
            )
        except Exception as e:
            logger.exception("Session start failed")
    else:
        logger.info(f"Session type '{session_type}' not found in DEFAULT_SESSION_CLASSES")  


@shared_task(
    bind=True,
    name="training_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def training_task_wrapper(self, dataset_settings_dict, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email):
    training_task(
        dataset_settings_dict,
        model_id,
        graph_spec_dict,
        training_session_id,
        training_settings,
        load_checkpoint,
        user_email,
        is_retry=(self.request.retries > 0),                
    )


class CeleryTaskExecutor(TaskExecutor):
    def __init__(self, app=CELERY_APP):
        self._app = app
    
    def enqueue(self, task_name, *args, **kwargs):
        self._app.tasks[task_name].delay(*args, **kwargs)
