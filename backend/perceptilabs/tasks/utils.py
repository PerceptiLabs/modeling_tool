import perceptilabs.settings as settings
from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor


def get_task_executor():
    if settings.CELERY:
        return CeleryTaskExecutor()
    else:
        return ThreadedTaskExecutor()
