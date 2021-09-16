from celery.result import AsyncResult
from celery import Celery, shared_task
import logging
import requests

from perceptilabs.endpoints.session.base_executor import BaseExecutor
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.endpoints.session.utils as session_utils
import perceptilabs.settings as settings

logger = logging.getLogger(APPLICATION_LOGGER)

celery_app = Celery(
    'training',
    backend=settings.CELERY_REDIS_URL,
    broker=settings.CELERY_REDIS_URL,
    imports=('perceptilabs',),
    task_routes={
        'session_task': {
            'queue': 'training'
        }
    }
)

@shared_task(bind=True,
          name="session_task",
          autoretry_for=(Exception,),
          default_retry_delay=5,
          max_retries=3,
)
def session_task(self, task_type, user_email, receiver, start_payload):

    def on_task_started(port):
        self.update_state(
            state='STARTED',
            meta={'hostname': self.request.hostname, 'port': port, 'user_email': user_email, 'receiver': receiver, 'task_type': task_type},
        )

    # TODO: start a thread that polls for cancelation
    # when detected, trigger the cancel_token

    logger.info(f"Received session_task for {user_email}/{receiver}")


    session = session_utils.Session.from_type(task_type)
    session.start(
        start_payload,
        is_retry=(self.request.retries > 0),        
        on_task_started=on_task_started
    )

class CeleryExecutor(BaseExecutor):
    def __init__(self, app=celery_app):
        self._app = app
        self._session_task = app.tasks["session_task"]
        assert self._app
        assert self._session_task

    def is_available(self):
        result = self._inspect_tasks().ping()
        return result is not None

    def start_task(self, task_type, user_email, model_id, payload):
        existing = self._get_celery_task(user_email, model_id)
        if existing is not None:
            existing.revoke(terminate=True)

        task = self._session_task.delay(task_type, user_email, model_id, payload)
        logger.info(f"Enqueued task for {user_email}, model {model_id}")
        return {
            "model_id": model_id,
            "user_email": user_email,
            "session_id": task.id,
        }

    def get_workers(self):
        def worker_hostname(celery_worker_name):
            if not celery_worker_name:
                return celery_worker_name

            return celery_worker_name.split("@")[-1]

        insp = self._app.control.inspect().ping()
        if not insp:
            return [];

        return [{"host": worker_hostname(k)} for k in insp.keys()]


    def cancel_task(self, user_email, model_id):
        self.send_request(user_email, model_id, "Stop", {"action": "Stop"})

    def send_request(self, user_email, model_id, action, data):

        info = self.get_task_info(user_email, model_id)

        if not info:
            return {}

        try:
            celery_host = info['hostname']
            if not celery_host:
                raise Exception(f"Unknown host for task for {user_email}/{model_id}")

            hostname = celery_host.split("@")[-1]

            port = info['port']
            url = f'http://{hostname}:{port}/'
            response = requests.post(url, json=data, timeout=5)  # Forward request to worker
            if response.ok:
                return response.json()
            else:
                raise Exception(f"Received status code {response.status_code} from {url}")
        except requests.exceptions.ReadTimeout as e:
            raise Exception(f"Timeout while waiting for the result of action '{action}' from the training thread. Request: {data}")
        except Exception as e:
            logger.exception(e)
            raise e

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
        active_method = self._inspect_tasks().active
        active = self._inspect_tasks().active() or {}
        insp = self._app.control.inspect()

        for tasks in active.values():
            for task in tasks:
                yield AsyncResult(task['id'], app=self._app)

    def _inspect_tasks(self):
        return self._app.control.inspect()
