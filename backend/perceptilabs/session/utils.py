import logging

from perceptilabs.session.base import Session
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.settings as settings


logger = logging.getLogger(APPLICATION_LOGGER)

from perceptilabs.serving.gradio_serving import GradioSession


DEFAULT_SESSION_CLASSES = {
    'gradio-session': GradioSession
}


def get_threaded_session_executor(single_threaded=False):
    from perceptilabs.session.threaded_executor import ThreadedExecutor
    return ThreadedExecutor(
        single_threaded=single_threaded, session_classes=DEFAULT_SESSION_CLASSES)


def get_session_executor():
    from perceptilabs.session.celery_executor import CeleryExecutor

    if settings.CELERY:
        logger.info("Using Celery executor for training/testing tasks...")
        return CeleryExecutor()
    else:
        logger.info("Using Threaded executor for training/testing tasks...")
        return get_threaded_session_executor()
