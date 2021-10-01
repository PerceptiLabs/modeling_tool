from celery.result import AsyncResult
from celery import Celery, shared_task
import logging
import requests
import functools

from perceptilabs.session.base import BaseExecutor
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.session.utils as session_utils
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

        
class CeleryExecutor(BaseExecutor):
    def __init__(self, app=celery_app):
        self._app = app
        self._session_task = app.tasks["session_task"]
        assert self._app
        assert self._session_task

    def cancel_session(self, session_id, payload=None):
        payload = payload or {}

        try:
            # try to send an initial stop request.
            self.send_request(session_id, payload)
        except:
            pass

        result = AsyncResult(session_id, app=self._app)        
        if result is not None:
            result.revoke(terminate=True)
    
    def get_sessions(self, predicate=None):
        if predicate is None:
            predicate = lambda x, y: True  # Get all sessions
        
        sessions = {}
        for celery_result in self._get_celery_tasks():
            session_id = celery_result.id
            metadata = celery_result.info
            
            if predicate(session_id, metadata):
                sessions[session_id] = metadata
                
        return sessions

    def get_session_hostname(self, session_id):
        meta = self.get_session_meta(session_id)
        hostname = meta['hostname'].split("@")[-1]  # split celery hostname
        return hostname

    def start_session(self, session_type, payload):
        task = self._session_task.delay(session_type, payload)
        logger.info(f"Enqueued task for session type '{session_type}'")
        return task.id

    def is_available(self):
        result = self._inspect_tasks().ping()
        return result is not None

    def get_workers(self):
        def worker_hostname(celery_worker_name):
            if not celery_worker_name:
                return celery_worker_name

            return celery_worker_name.split("@")[-1]

        insp = self._app.control.inspect().ping()
        if not insp:
            return [];

        return [{"host": worker_hostname(k)} for k in insp.keys()]

    def get_session_meta(self, session_id):
        result = AsyncResult(session_id, app=self._app)        
        return result.info

    def _get_celery_tasks(self):
        active = self._inspect_tasks().active() or {}

        for tasks in active.values():
            for task in tasks:
                result = AsyncResult(task['id'], app=self._app)
                if result.info is None:
                    continue
                yield result
        
    def _inspect_tasks(self):
        return self._app.control.inspect()

    def dispose(self):
        pass
