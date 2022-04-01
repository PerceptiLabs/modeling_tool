import pytest
from monitor.predictions import get_predictions


def test_empty():
    ret = get_predictions([])
    assert not ret


@pytest.fixture
def config(mocker):
    ret = {
        "expected_sec_per_task": 26,
        "max_wait_time_sec": 100,
        "worker_type": "the_worker_type",
    }
    mocker.patch("monitor.predictions._get_task_config", return_value=ret)
    worker_config = "the-worker-deployment"
    mocker.patch(
        "monitor.predictions._deployment_for_worker_type", return_value=worker_config
    )
    return True


@pytest.fixture
def task():
    return {
        "queue": "the_queue_name",
        "name": "the_task_name",
    }


@pytest.mark.parametrize("num_tasks,expected", [(1, 1), (5, 2)])
def test_simple(config, task, num_tasks, expected):
    tasks = [task] * num_tasks
    ret = get_predictions(tasks)
    assert ret == {"the-worker-deployment": expected}
