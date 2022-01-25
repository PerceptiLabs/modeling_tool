import os
import pytest
from retrying import retry
from unittest.mock import MagicMock

from celery import shared_task
from celery.contrib.pytest import (
    celery_worker, celery_app, celery_config,
    celery_parameters, celery_enable_logging,
    use_celery_app_trap, celery_includes,
    celery_worker_pool, celery_worker_parameters
)

from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor


@pytest.fixture(scope='function')
def callbacks():
    return MagicMock()


@pytest.fixture(scope='session')
def celery_config():
    return {
        'worker_send_task_events': True,
        'task_send_sent_event': False
    }


@pytest.fixture(scope='function')
def executor(mode, celery_app, celery_worker, callbacks):
    def hello_task():
        print("HELLO!!!")

    def crash_task():
        raise ValueError("CRASH!!!")

    if mode == 'threaded':
        return ThreadedTaskExecutor(
            tasks={
                'hello_task': hello_task,
                'crash_task': crash_task
            },
            on_task_sent=callbacks.on_task_sent,
            on_task_received=callbacks.on_task_received,
            on_task_started=callbacks.on_task_started,            
            on_task_succeeded=callbacks.on_task_succeeded,
            on_task_failed=callbacks.on_task_failed
        )
    elif mode == 'celery':
        @celery_app.task(name='hello_task')
        def wrap_hello():
            return hello_task()

        @celery_app.task(name='crash_task')
        def wrap_crash():
            return crash_task()

        celery_worker.reload()
        
        return CeleryTaskExecutor(
            app=celery_app,
            on_task_sent=callbacks.on_task_sent,
            on_task_received=callbacks.on_task_received,
            on_task_started=callbacks.on_task_started,            
            on_task_succeeded=callbacks.on_task_succeeded,
            on_task_failed=callbacks.on_task_failed
        )
    else:
        raise ValueError

    
@pytest.mark.parametrize('mode', ['threaded', 'celery'])
def test_success(executor, callbacks):
    task_name = 'hello_task'
    task_id = executor.enqueue(task_name)

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_task():
        callbacks.on_task_sent.assert_called_once()
        assert callbacks.on_task_sent.call_args[0][0:2] == (task_id, task_name)
    
        callbacks.on_task_received.assert_called_once()
        assert callbacks.on_task_received.call_args[0][0:2] == (task_id, task_name)
        
        callbacks.on_task_started.assert_called_once()
        assert callbacks.on_task_started.call_args[0][0:1] == (task_id,)
        
        callbacks.on_task_succeeded.assert_called_once()
        assert callbacks.on_task_succeeded.call_args[0][0:1] == (task_id,)

        assert callbacks.on_task_failed.call_count == 0

    wait_for_task()


@pytest.mark.parametrize('mode', ['threaded', 'celery'])
def test_failure(executor, callbacks, monkeypatch):
    task_name = 'crash_task'
    task_id = executor.enqueue(task_name)

    @retry(stop_max_attempt_number=10, wait_fixed=1000)
    def wait_for_task():
        callbacks.on_task_sent.assert_called_once()
        assert callbacks.on_task_sent.call_args[0][0:2] == (task_id, task_name)
    
        callbacks.on_task_received.assert_called_once()
        assert callbacks.on_task_received.call_args[0][0:2] == (task_id, task_name)
        
        callbacks.on_task_started.assert_called_once()
        assert callbacks.on_task_started.call_args[0][0:1] == (task_id,)

        assert callbacks.on_task_succeeded.call_count == 0
        
        callbacks.on_task_failed.assert_called_once()
        assert callbacks.on_task_failed.call_args[0][0:1] == (task_id,)

    wait_for_task()
    

