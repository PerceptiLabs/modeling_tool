from monitor.log import logged, logged_generator
from monitor.settings import CONFIG
from monitor.utils import aggregate_flat, hash_adder
import logging
import math


def _get_task_config(queue_name, task_name):
    return CONFIG["queues"][queue_name]["tasks"][task_name]


def _estimate_task(task):
    task_config = _get_task_config(task["queue"], task["name"])

    # TODO (long-term): calculate it from the size of the task
    expected_duration = task_config["expected_sec_per_task"]

    return {**task, "seconds_to_complete": expected_duration}


def _task_estimate_to_worker_estimate(task_estimate):
    queue_name = task_estimate["queue"]
    task_name = task_estimate["name"]
    task_config = _get_task_config(queue_name, task_name)
    return {**task_config, "seconds_to_complete": task_estimate["seconds_to_complete"]}


def _calc_scale(worker_type_estimate):
    s_to_complete = worker_type_estimate["seconds_to_complete"]
    max_concurrency = worker_type_estimate.get("max_concurrency", 1)
    seconds_for_one_worker = s_to_complete / max_concurrency
    max_wait = worker_type_estimate["max_wait_time_sec"]
    num_workers_float = seconds_for_one_worker / max_wait
    num_workers = math.ceil(num_workers_float)

    return {
        "worker_type": worker_type_estimate["worker_type"],
        "seconds_for_one_worker": seconds_for_one_worker,
        "num_workers_float": num_workers_float,
        "workers_needed": num_workers,
    }


def _deployment_for_worker_type(worker_type):
    return CONFIG["worker_types"][worker_type]["deployment"]


@logged_generator(logging.DEBUG, "worker_estimates_per_type:")
def _worker_estimates_per_type(worker_estimates_per_task):
    return aggregate_flat(
        worker_estimates_per_task, ["worker_type"], hash_adder("seconds_to_complete")
    )


@logged_generator(logging.DEBUG, "scales_per_type:")
def _scales_per_type(worker_estimates_per_type):
    return [_calc_scale(w) for w in worker_estimates_per_type]


@logged(logging.INFO, "scales_per_deployment:")
def get_predictions(tasks):
    task_estimates = [_estimate_task(t) for t in tasks]
    worker_estimates_per_task = [
        _task_estimate_to_worker_estimate(t) for t in task_estimates
    ]
    per_type = _worker_estimates_per_type(worker_estimates_per_task)
    scales_by_type = _scales_per_type(per_type)
    return {
        _deployment_for_worker_type(s["worker_type"]): s["workers_needed"]
        for s in scales_by_type
    }
