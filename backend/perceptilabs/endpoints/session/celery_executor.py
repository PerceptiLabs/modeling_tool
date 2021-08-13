from celery.result import AsyncResult
import celery
import logging

from perceptilabs.endpoints.session.base_executor import BaseExecutor
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.session.utils as session_utils
import perceptilabs.settings as settings

logger = logging.getLogger(APPLICATION_LOGGER)

celery_app = celery.Celery(
    'training',
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    imports=('perceptilabs',),
    task_routes={
        'perceptilabs.endpoints.session.celery_executor': {
            'queue': 'training'
        }
    }
)

@celery_app.task(bind=True,
          name="session_task",
          autoretry_for=(Exception,),
          default_retry_delay=5,
          max_retries=3,
)
def session_task(self, user_email, receiver, start_payload):

    def on_server_started(hostname, port):
        self.update_state(
            state='STARTED',
            meta={'hostname': self.request.hostname, 'port': port, 'ip': hostname, 'user_email': user_email, 'receiver': receiver},
        )

    # TODO: start a thread that polls for cancelation
    # when detected, trigger the cancel_token

    session_utils.run_kernel(
        start_payload,
        on_server_started=on_server_started,
        is_retry=(self.request.retries > 0)
    )

class CeleryExecutor(BaseExecutor):
    def __init__(self, app=celery_app):
        self._app = app
        self._session_task = app.tasks["session_task"]

    def is_available(self):
        result = self._inspect_tasks().ping()
        return result is not None

    def start_task(self, user_email, model_id, payload):
        existing = self._get_celery_task(user_email, model_id)
        if existing is not None:
            existing.revoke(terminate=True)

        task = self._session_task.delay(user_email, model_id, payload)
        logger.info(f"Enqueued task for {user_email}, model {model_id}")
        return {
            "model_id": model_id,
            "user_email": user_email,
            "session_id": task.id,
        }

    def cancel_task(self, user_email, model_id):
        celery_task = self._get_celery_task(user_email, model_id)

        if not celery_task:
            return None

        # TODO
        pass

    def get_task_info(self, task_id, model_id):
        celery_task = self._get_celery_task(task_id, model_id)

        if celery_task is None:
            return None
        else:
            return celery_task.info

    def get_active_tasks(self, user_email):
        return {
            celery_task.id: celery_task.info
            for celery_task in self._get_celery_tasks(user_email)
        }

    def _get_celery_task(self, user_email, model_id):
        for celery_task in self._get_celery_tasks(user_email):
            if str(celery_task.info['receiver']) == str(model_id):
                return celery_task
        return None

    def _get_celery_tasks(self, user_email):
        for result in self._active_celery_results():
            if result.info and result.info['user_email'] == user_email:
                yield result

    def _active_celery_results(self):
        active = self._inspect_tasks().active() or {}

        for tasks in active.values():
            for task in tasks:
                yield AsyncResult(task['id'], app=self._app)

    def _inspect_tasks(self):
        return self._app.control.inspect()
