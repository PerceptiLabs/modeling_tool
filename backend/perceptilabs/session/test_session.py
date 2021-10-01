import os
import time

import pytest
from unittest.mock import MagicMock
from retrying import retry

from perceptilabs.session.base import Session
from perceptilabs.session.threaded_executor import ThreadedExecutor
from perceptilabs.session.celery_executor import CeleryExecutor
from perceptilabs.utils import is_azure_pipelines
import perceptilabs.session.utils as session_utils
from celery.contrib.pytest import (
    celery_worker, celery_app, celery_config, celery_parameters, celery_enable_logging, use_celery_app_trap, celery_includes, celery_worker_pool, celery_worker_parameters
)


def skip_in_ci(value, reason=""):
    # TODO: these tests should really work on the build pipeline, but for now make them just work locally    
    return pytest.param(
        value,
        marks=pytest.mark.skipif(
            is_azure_pipelines(),
            reason=reason
        )
    )


class DummySession(Session):
    has_finished = True  # We only care whether the callbacks have been called. Exit asap
    on_start_called = MagicMock()
    on_request_received = MagicMock()

    
@pytest.fixture(scope='function')
def threaded_executor():  
    executor = ThreadedExecutor(
        single_threaded=False,
        session_classes={'dummy-session': DummySession}
    )
    yield executor
    executor.dispose()  # Cancel existing tasks...

    
@pytest.fixture(scope='session')
def celery_enable_logging():
    return True


@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'threads'


@pytest.fixture(scope='function')
def celery_executor(celery_worker):  
    session_utils.DEFAULT_SESSION_CLASSES['dummy-session'] = DummySession  # the celery task uses the global list...
    executor = CeleryExecutor(app=celery_worker.app)

    # workaround from https://github.com/celery/celery/issues/3642#issuecomment-369057682
    # in which the tasks aren't registered in the worker
    celery_worker.reload()    
    yield executor


@pytest.fixture
def executor(request, threaded_executor, celery_executor):
    if request.param == 'threaded':
        yield threaded_executor
    elif request.param == 'celery':
        yield celery_executor
        

@retry(stop_max_attempt_number=10, wait_fixed=2000)
def wait_for_session(executor, session_id):
    ret = executor.get_sessions()
    assert session_id in ret


@retry(stop_max_attempt_number=10, wait_fixed=2000)
def wait_for_session_not_present(executor, session_id):
    ret = executor.get_sessions()
    assert session_id not in ret

    
@pytest.mark.parametrize(
    "executor", ["threaded", skip_in_ci("celery", reason="Flaky")], indirect=True
)
def test_start_session(executor):
    payload = {'key1': 'value1', 'key2': 'value2'}
    session_id = executor.start_session('dummy-session', payload)
    wait_for_session(executor, session_id)
    
    assert DummySession.on_start_called.called
    assert DummySession.on_start_called.call_args.args == (payload, False)

    metadata = executor.get_sessions().get(session_id, {})
    assert 'port' in metadata
    assert 'hostname' in metadata
    assert metadata['payload'] == payload
    assert metadata['type'] == 'dummy-session'
    

@pytest.mark.parametrize(
    "executor", ["threaded", skip_in_ci("celery", reason="Flaky")], indirect=True
)
def test_send_request(executor):
    expected_payload = {'key3': 'value3', 'key4': 'value4'}    
    expected_response = {'key5': 'value5', 'key6': 'value6'}
    DummySession.on_request_received.return_value = expected_response

    session_id = executor.start_session('dummy-session', {})
    wait_for_session(executor, session_id)

    actual_response = executor.send_request(session_id, expected_payload)
    
    assert DummySession.on_request_received.called
    assert DummySession.on_request_received.call_args.args == (expected_payload,)
    assert actual_response == expected_response
    

@pytest.mark.parametrize(
    "executor", ["threaded", skip_in_ci("celery", reason="Flaky")], indirect=True
)
def test_cancel_session(executor):
    session_id = executor.start_session('dummy-session', {})
    wait_for_session(executor, session_id)

    expected_payload = {'key3': 'value3', 'key4': 'value4'}        
    executor.cancel_session(session_id, expected_payload)
    
    assert DummySession.on_request_received.called
    assert DummySession.on_request_received.call_args.args == (expected_payload,)

    wait_for_session_not_present(executor, session_id)


@pytest.mark.parametrize(
    "executor", ["threaded", skip_in_ci("celery", reason="Flaky")], indirect=True
)
def test_active_tasks_with_predicate(executor):
    assert executor.get_sessions() == {}

    start_payload = {'key': 'value'}
    session_id = executor.start_session('dummy-session', start_payload)
    wait_for_session(executor, session_id)

    def predicate1(session_id, metadata):
        return metadata['payload'] == start_payload

    assert session_id in executor.get_sessions(predicate=predicate1)

    def predicate2(session_id, metadata):
        return metadata['payload'] != start_payload
    
    assert session_id not in executor.get_sessions(predicate=predicate2)    



