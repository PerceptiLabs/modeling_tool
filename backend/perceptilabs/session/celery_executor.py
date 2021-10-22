from celery.result import AsyncResult
from celery import Celery, shared_task
import logging

from perceptilabs.session.base import BaseExecutor
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.session.utils as session_utils
import perceptilabs.settings as settings
from perceptilabs.tasks.celery_executor import CELERY_APP
        
logger = logging.getLogger(APPLICATION_LOGGER)

        
class CeleryExecutor(BaseExecutor):
    def __init__(self, app=CELERY_APP):
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
