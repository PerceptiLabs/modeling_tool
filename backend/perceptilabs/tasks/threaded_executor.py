import uuid
from threading import RLock
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

from perceptilabs.tasks.base import TaskExecutor
import perceptilabs.tasks.base as tasks


DEFAULT_TASKS = {
    "training_task": tasks.training_task,
    "testing_task": tasks.testing_task,
    "serving_task": tasks.serving_task,
    "preprocessing_task": tasks.preprocessing_task,
}


class ThreadedTaskExecutor(TaskExecutor):
    def __init__(
        self,
        tasks=DEFAULT_TASKS,
        on_task_sent=None,
        on_task_received=None,
        on_task_started=None,
        on_task_succeeded=None,
        on_task_failed=None,
    ):
        self._task_functions = tasks
        self._pool = ThreadPoolExecutor()
        self._submitted_tasks = {}
        self._lock = RLock()

        self._on_task_sent = on_task_sent
        self._on_task_received = on_task_received
        self._on_task_started = on_task_started
        self._on_task_succeeded = on_task_succeeded
        self._on_task_failed = on_task_failed

    def enqueue(self, task_name, *args, **kwargs):
        task_id = uuid.uuid4().hex

        if self._on_task_sent:
            self._on_task_sent(task_id, task_name)

        task_func = self._task_functions[task_name]
        task_func_with_callbacks = self._wrap_in_callbacks(
            task_func, task_id, task_name
        )

        future = self._pool.submit(task_func_with_callbacks, *args, **kwargs)

        with self._lock:
            self._submitted_tasks[task_id] = {
                "future": future,
                "args": deepcopy(args),
                "kwargs": deepcopy(kwargs),
            }

        return task_id

    def _wrap_in_callbacks(self, task_func, task_id, task_name):
        def task_func_with_callbacks(*args, **kwargs):
            if self._on_task_received:
                self._on_task_received(task_id, task_name)

            if self._on_task_started:
                self._on_task_started(task_id)

            try:
                result = task_func(*args, **kwargs)
            except:
                if self._on_task_failed:
                    self._on_task_failed(task_id)
                raise
            else:
                if self._on_task_succeeded:
                    self._on_task_succeeded(task_id)

                return result

        return task_func_with_callbacks

    @property
    def num_remaining_tasks(self):
        count = 0
        with self._lock:
            for task_info in self._submitted_tasks.values():
                if not task_info["future"].done():
                    count += 1
        return count

    def get_tasks(self):
        result = {}
        with self._lock:
            results = {
                task_id: {
                    "args": deepcopy(task_info["args"]),
                    "kwargs": deepcopy(task_info["kwargs"]),
                }
                for task_id, task_info in self._submitted_tasks.items()
                if not task_info["future"].done()
            }
        return results
