from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event

from perceptilabs.endpoints.session.base_executor import BaseExecutor
import perceptilabs.endpoints.session.utils as session_utils
from perceptilabs.utils import DummyExecutor

class ThreadedTask:
    def __init__(self, make_future):
        self._token = Event()
        self._future = make_future(self._token)
        self._meta = None

    def __del__(self):
        if self._token:
            self._token.set()
            self._token = None

        if self._future:
            ret = self._future.cancel()
            self._future = None

    def get_metadata(self):
        return self._meta

    def set_metadata(self, **kwargs):
        self._meta=kwargs

# Thread-interlocked cache of task-related metadata
class TaskCache:
    def __init__(self):
        self._tasks = {}
        self._lock = Lock()

    def dispose(self):
        with self._lock:
            while self._tasks:
                first_key = list(self._tasks.keys())[0]
                del self._tasks[first_key]

    def add(self, id, make_future):
        # thread-unsafe pre-clear of the cache for perf
        if id in self._tasks:  # Delete existing
            with self._lock:
                del self._tasks[id]

        # thread-safe upsert of cache value for correctness
        with self._lock:
            if id in self._tasks:
                del self._tasks[id]
            self._tasks[id] = ThreadedTask(make_future)

    def set_metadata(self, id, **kwargs):
        with self._lock:
            self._tasks[id].set_metadata(**kwargs)

    def set_exception(self, id, exception):
        with self._lock:
            self._tasks[id].set_metadata(exception=exception)

    def set_complete(self, id):
        with self._lock:
            self._tasks[id] = None


    def cancel_task(self, id):
        with self._lock:
            task = self._tasks.get(id)
            if not task:
                return None

            del self._tasks[id]
            return task.get_metadata()

    def get(self, id):
        with self._lock:
            task = self._tasks.get(id)
            if not task:
                return None
            meta = task.get_metadata()

            if "exception" in meta:
                raise meta["exception"]

            return meta

    def get_active(self, predicate):
        with self._lock:
            ret = {
                key: value.get_metadata().copy()
                for key, value in self._tasks.items() if predicate(key) and value.get_metadata()
            }
            return ret

class ThreadedExecutor(BaseExecutor):
    def __init__(self, single_threaded=False):
        self._pool = DummyExecutor() if single_threaded else ThreadPoolExecutor()
        self._task_cache = TaskCache()

    def dispose(self):
        if self._pool and isinstance(self._pool, ThreadPoolExecutor):
            self._pool.shutdown(wait=False)
            self._pool = None

        if self._task_cache:
            self._task_cache.dispose()
            self._task_cache = None

    def start_task(self, user_email, model_id, payload):
        task_id = self._format_task_id(user_email, model_id)

        def run_task(cancel_token):
            try:
                def on_server_started(hostname, port):
                    self._task_cache.set_metadata(task_id, port=port, hostname=hostname)

                session_utils.run_kernel(payload, on_server_started=on_server_started, cancel_token=cancel_token)
                self._task_cache.set_complete(task_id)
            except Exception as e:
                self._task_cache.set_exception(task_id, e)

        run_with_token = lambda token: self._pool.submit(run_task, token)
        self._task_cache.add(task_id, run_with_token)

        return {
            "model_id": model_id,
            "user_email": user_email,
            "session_id": task_id,
        }

    def cancel_task(self, user_email, model_id):
        task_id = self._format_task_id(user_email, model_id)
        self._task_cache.cancel_task(task_id)

    def get_task_info(self, user_email, model_id):
        task_id = self._format_task_id(user_email, model_id)
        ret = self._task_cache.get(task_id)
        return ret

    def get_active_tasks(self, user_email):
        def matches_email(key):
            ret = key.startswith(user_email)
            return ret

        ret = self._task_cache.get_active(matches_email)
        return ret

    def _format_task_id(self, user_email, model_id):
        return f"{user_email}/{model_id}"

