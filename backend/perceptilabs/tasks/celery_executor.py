import logging
from celery import Celery, shared_task


import perceptilabs.settings as settings
from perceptilabs.tasks.base import (
    TaskExecutor,
    training_task,
    testing_task,
    serving_task,
    preprocessing_task        
)


logger = logging.getLogger(__name__)


CELERY_APP = Celery(
    'training',
    backend=settings.CELERY_REDIS_URL,
    broker=settings.CELERY_REDIS_URL,
    imports=('perceptilabs',),
    task_routes={
        'training_task': {'queue': 'training'},
        'testing_task': {'queue': 'training'},
        'serving_task': {'queue': 'training'},
        'preprocessing_task': {'queue': 'training'}                
    }
)

@shared_task(
    bind=True,
    name="training_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def training_task_wrapper(self, dataset_settings_dict, model_id, graph_spec_dict, training_session_id, training_settings, load_checkpoint, user_email, logrocket_url=''):
    training_task(
        dataset_settings_dict,
        model_id,
        graph_spec_dict,
        training_session_id,
        training_settings,
        load_checkpoint,
        user_email,
        is_retry=(self.request.retries > 0),
        logrocket_url=logrocket_url
    )

@shared_task(
    bind=True,
    name="testing_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def testing_task_wrapper(self, *args, **kwargs):
    testing_task(*args, **kwargs)


@shared_task(
    bind=True,
    name="serving_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def serving_task_wrapper(self, *args, **kwargs):
    serving_task(*args, **kwargs)


@shared_task(
    bind=True,
    name="preprocessing_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def preprocessing_task_wrapper(self, *args, **kwargs):
    preprocessing_task(*args, **kwargs)
    
    
class CeleryTaskExecutor(TaskExecutor):
    def __init__(self, app=CELERY_APP):
        self._app = app
    
    def enqueue(self, task_name, *args, **kwargs):
        self._app.tasks[task_name].delay(*args, **kwargs)
