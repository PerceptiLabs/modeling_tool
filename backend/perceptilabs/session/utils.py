# TODO: move TestingSession&TrainingSession into some better location
import logging


from perceptilabs.mainInterface import Interface
from perceptilabs.issues import IssueHandler
from perceptilabs.session.base import Session
from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.settings as settings


logger = logging.getLogger(APPLICATION_LOGGER)


class TestingSession(Session):
    def __init__(self):
        self._has_finished = False
        self._has_failed = False

        issue_handler = IssueHandler()
        cores = dict()
        testcore = None
        
        self._main_interface = Interface(
            cores, testcore, issue_handler,
            session_id='123', allow_headless=False)
    
    def on_request_received(self, request):
        response = self._main_interface.create_response_with_errors(request)        
        return response
    
    def on_start_called(self, start_payload, is_retry):
        def on_finished(failed=False):
            self._has_finished = True
            self._has_failed = failed

        self._main_interface.create_response(
            start_payload, is_retry=is_retry, on_finished=on_finished)  # Start training/testing

    @property
    def has_finished(self):
        return self._has_finished

    @property
    def has_failed(self):
        return self._has_failed

    
from perceptilabs.serving.gradio_serving import GradioSession


DEFAULT_SESSION_CLASSES = {
    'training-session': TestingSession,  # TODO(anton.k): decouple and simplify!
    'testing-session': TestingSession,  
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
