import pytest
from celery.contrib.pytest import *
from retrying import retry
from threading import Event

import perceptilabs.endpoints.session.utils
from perceptilabs.endpoints.session.celery_executor import CeleryExecutor

@pytest.fixture
def completion_event():
    return Event()


@pytest.fixture(scope='function')
def executor(celery_worker, completion_event, monkeypatch):
    # monkeypatch.setattr(perceptilabs.endpoints.session.celery_executor, 'celery_app', celery_app)

    def fake_run_kernel(*args, **kwargs):
        kwargs["on_server_started"](00000)
        completion_event.wait(10)

    monkeypatch.setattr(perceptilabs.endpoints.session.utils, 'run_kernel', fake_run_kernel)

    ret = CeleryExecutor(app=celery_worker.app)

    # workaround from https://github.com/celery/celery/issues/3642#issuecomment-369057682
    # in which the tasks aren't registered in the worker
    celery_worker.reload()

    return ret

@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'worker_state_db': 'state',
    }

def test_is_available(executor):
    assert executor.is_available()


def test_get_task_info_returns_empty_with_mismatched_params(executor):
    ret = executor.get_active_tasks("no@email")
    assert not ret

@retry(stop_max_attempt_number=5, wait_fixed=2000)
def wait_for_active_task(executor):
    ret = executor.get_active_tasks("a@b")
    assert ret


# TODO: the celery pytest plugin doesn't work because the task metadata cache is not shared between worker and main threads
# Find a way around that so we can get a working test
@pytest.mark.skip
@pytest.mark.celery(task_always_eager=True)
def test_get_task_info_with_matching_email(executor, celery_worker, completion_event):
    executor.start_task("a@b", 123, {})

    try:
        wait_for_active_task(executor)
    finally:
        completion_event.set()

    # Test that there are no tasks after
    ret = executor.get_active_tasks("a@b")
    assert not ret

# Prototype for testing a task run
# def test_create_task(celery_app, celery_worker):
#     @celery_app.task(name="mm")
#     def mul(x, y):
#         return x * y
#
#     # workaround from https://github.com/celery/celery/issues/3642#issuecomment-369057682
#     # in which the tasks aren't registered in the worker
#     celery_worker.reload()
#
#     task = celery_app.tasks['mm']
#     assert task.delay(4, 4).get(timeout=10) == 16
