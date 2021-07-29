from concurrent.futures import ThreadPoolExecutor

from perceptilabs.endpoints.session.base_executor import BaseExecutor
import perceptilabs.endpoints.session.utils as session_utils
from perceptilabs.utils import DummyExecutor



class ThreadedExecutor(BaseExecutor):    
    def __init__(self, single_threaded=False):
        self._pool = DummyExecutor() if single_threaded else ThreadPoolExecutor()
        self._futures = {}
        self._meta = {}

    def start_task(self, user_email, model_id, payload):
        task_id = self._format_task_id(user_email, model_id)        
        if task_id in self._meta:  # Delete existing
            del self._meta[task_id]
        
        def task():
            def on_server_started(hostname, port):
                self._meta[task_id] = {'port': port, 'hostname': hostname}
                
            session_utils.run_kernel(payload, on_server_started=on_server_started)

        self._futures[task_id] = self._pool.submit(task)
        return task_id

    def get_task_info(self, user_email, model_id):
        task_id = self._format_task_id(user_email, model_id)
        return self._meta.get(task_id)

    def get_active_tasks(self, user_email):
        return {
            key: value.copy()
            for key, value in self._meta.items() if key.startswith(user_email)
        }
        
    def _format_task_id(self, user_email, model_id):
        return f"{user_email}/{model_id}"
    
