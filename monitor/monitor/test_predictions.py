from debug_print import _d
import pytest
from monitor.predictions import Predictor

from monitor.config import Config


@pytest.fixture
def config():
    return Config(
        {
            "queues": {
                "the_queue_name": {
                    "tasks": {
                        "the_task_name": {
                            "expected_sec_per_task": 26,
                            "max_wait_time_sec": 100,
                            "worker_type": "the_worker_type",
                        },
                    },
                },
            },
            "worker_types": {
                "the_worker_type": {"deployment": "the-worker-deployment"}
            },
        }
    )


@pytest.fixture
def task():
    return {
        "queue": "the_queue_name",
        "name": "the_task_name",
    }


def test_empty(config):
    ret = Predictor(config).get_predictions([])
    assert not ret


@pytest.mark.parametrize("num_tasks,expected", [(1, 1), (5, 2)])
def test_simple(config, task, num_tasks, expected):
    tasks = [task] * num_tasks
    ret = Predictor(config).get_predictions(tasks)
    assert ret == {"the-worker-deployment": expected}


def test_extra_queue(config, task):
    unrelated_task = {
        "queue": "unrelated queue",
        "name": "another task",
    }
    tasks = [task, unrelated_task]
    ret = Predictor(config).get_predictions(tasks)
    assert ret == {"the-worker-deployment": 1}
