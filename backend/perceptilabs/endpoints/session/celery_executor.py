import celery
from celery.result import AsyncResult

from perceptilabs.endpoints.session.base_executor import BaseExecutor
import perceptilabs.endpoints.session.utils as session_utils
import perceptilabs.settings as settings


celery_app = celery.Celery(
    'tasks',
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    imports=('perceptilabs',)
)


@celery_app.task(bind=True)
def session_task(self, receiver, start_payload):
    try:
        def on_server_started(hostname, port):
            self.update_state(
                state='STARTED', meta={'hostname': self.request.hostname, 'port': port, 'ip': hostname, 'receiver': receiver})  # TODO: user email here...
        session_utils.run_kernel(
            start_payload,
            on_server_started=on_server_started,
            is_retry=(self.request.retries > 0)
        )
    except Exception as e:
        self.retry(max_retries=3, countdown=5)
        

class CeleryExecutor(BaseExecutor):
    @staticmethod
    def is_available(): 
        inspect = celery_app.control.inspect()
        result = inspect.ping() 
        return result is not None        
    
    def start_task(self, user_email, model_id, payload):
        existing = self._get_celery_task(user_email, model_id)
        if existing is not None:
            existing.revoke(terminate=True)
        
        session_task.delay(model_id, payload)
        return model_id

    def get_task_info(self, user_email, model_id):
        celery_task = self._get_celery_task(user_email, model_id)
        
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
        for hostname, tasks in celery_app.control.inspect().active().items():
            for task in tasks:
                result = AsyncResult(task['id'], app=celery_app)
                #if result.info['user_email'] == user_email:  # TODO: fix this
                yield result

    
