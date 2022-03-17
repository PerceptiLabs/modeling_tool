import logging
import threading
from celery import Celery, shared_task
from celery.result import AsyncResult


import perceptilabs.settings as settings
from perceptilabs.tasks.base import (
    TaskExecutor,
    training_task,
    testing_task,
    serving_task,
    preprocessing_task,
)


logger = logging.getLogger(__name__)


CELERY_APP = Celery(
    'training',
    backend=settings.CELERY_REDIS_URL,
    broker=settings.CELERY_REDIS_URL,
    imports=('perceptilabs',),
    worker_send_task_events=True,
    task_send_sent_event=False,
    task_routes={
        'training_task': {'queue': 'training'},
        'testing_task': {'queue': 'training'},
        'serving_task': {'queue': 'training'},
        'preprocessing_task': {'queue': 'training'},
    }
)

@shared_task(
    bind=True,
    name="training_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def training_task_wrapper(self, call_context, dataset_settings_dict, model_id, training_session_id, training_settings, load_checkpoint, logrocket_url='', graph_settings=None):
    training_task(
        call_context,
        dataset_settings_dict,
        model_id,
        training_session_id,
        training_settings,
        load_checkpoint,
        is_retry=(self.request.retries > 0),
        logrocket_url=logrocket_url,
        graph_settings=graph_settings
    )

@shared_task(
    bind=True,
    name="testing_task",
    autoretry_for=(Exception,),
    default_retry_delay=5,
    max_retries=3,
)
def testing_task_wrapper(self, call_context, *args, **kwargs):
    testing_task(call_context, *args, **kwargs)


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
    def __init__(
            self,
            app=CELERY_APP,
            on_task_sent=None,
            on_task_received=None,
            on_task_started=None,
            on_task_succeeded=None,
            on_task_failed=None
    ):
        self._app = app

        self._on_task_sent = on_task_sent
        self._on_task_received = on_task_received
        self._on_task_started = on_task_started
        self._on_task_succeeded = on_task_succeeded
        self._on_task_failed = on_task_failed

        self._monitoring_thread = self._setup_monitoring()

    def enqueue(self, task_name, *args, **kwargs):
        res = self._app.tasks[task_name].delay(*args, **kwargs)

        if self._on_task_sent:
            self._on_task_sent(res.id, task_name)

        return res.id

    def _setup_monitoring(self):
        def on_event(event):
            if event['type'] == 'task-sent' and self._on_task_sent:
                raise RuntimeError("This is handled in 'enqueue' for consistency")

            if event['type'] == 'task-received' and self._on_task_received:
                self._on_task_received(event['uuid'], event['name'])

            if event['type'] == 'task-started' and self._on_task_started:
                self._on_task_started(event['uuid'])

            if event['type'] == 'task-succeeded' and self._on_task_succeeded:
                self._on_task_succeeded(event['uuid'])

            if event['type'] == 'task-failed' and self._on_task_failed:
                self._on_task_failed(event['uuid'])

        def _worker():
            try:
                state = self._app.events.State()
                with self._app.connection() as conn:
                    recv = self._app.events.Receiver(conn, handlers={'*': on_event})
                    recv.capture(limit=None, timeout=None, wakeup=False)  # Blocks
            except:
                logger.exception("Exception in monitoring worker")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

        return thread

    @property
    def num_remaining_tasks(self):
        tasks = self._get_worker_tasks()
        return len(tasks)

    def _get_worker_tasks(self):
        as_dict = self._app.control.inspect().active() or {}

        tasks = []
        for worker_tasks in as_dict.values():
            tasks.extend(worker_tasks)

        return tasks

    def get_tasks(self):
        tasks = self._get_worker_tasks()

        results = {
            task['id']: {
                'args': tuple(task['args']),
                'kwargs': task['kwargs']
            }
            for task in tasks
        }
        return results
