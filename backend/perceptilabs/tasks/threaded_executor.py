from concurrent.futures import ThreadPoolExecutor

from perceptilabs.tasks.base import (
    TaskExecutor,
    training_task,
    testing_task,
    serving_task,
    preprocessing_task
)


class ThreadedTaskExecutor:
    def __init__(self):
        self._tasks = {
            'training_task': training_task,
            'testing_task': testing_task,
            'serving_task': serving_task,
            'preprocessing_task': preprocessing_task
        }        
        self._pool = ThreadPoolExecutor()

    def enqueue(self, task_name, *args, **kwargs):
        func = self._tasks[task_name]
        self._pool.submit(func, *args, **kwargs)


