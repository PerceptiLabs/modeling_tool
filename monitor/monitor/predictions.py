from monitor.log import logged, logged_generator
from monitor.settings import CONFIG
from monitor.utils import aggregate_flat, hash_adder
import logging
import math


class Predictor:
    def __init__(self, config):
        self._config = config

    @logged(logging.INFO, "scales_per_deployment:")
    def get_predictions(self, tasks):
        task_estimates = [self._estimate_task(t) for t in tasks]
        task_estimates = [t for t in task_estimates if t]
        worker_estimates_per_task = [
            self._task_estimate_to_worker_estimate(t) for t in task_estimates
        ]
        per_type = self._worker_estimates_per_type(worker_estimates_per_task)
        scales_by_type = self._scales_per_type(per_type)
        return {
            self._config.deployment_for_worker(s["worker_type"]): s["workers_needed"]
            for s in scales_by_type
        }

    def _estimate_task(self, task):
        task_config = self._config.for_task(task["queue"], task["name"])

        if not task_config:
            return None

        # TODO (long-term): calculate it from the size of the task
        expected_duration = task_config["expected_sec_per_task"]

        return {**task, "seconds_to_complete": expected_duration}

    def _task_estimate_to_worker_estimate(self, task_estimate):
        queue_name = task_estimate["queue"]
        task_name = task_estimate["name"]
        task_config = self._config.for_task(queue_name, task_name)
        return {
            **task_config,
            "seconds_to_complete": task_estimate["seconds_to_complete"],
        }

    @logged_generator(logging.DEBUG, "worker_estimates_per_type:")
    def _worker_estimates_per_type(self, worker_estimates_per_task):
        return aggregate_flat(
            worker_estimates_per_task,
            ["worker_type"],
            hash_adder("seconds_to_complete"),
        )

    @logged_generator(logging.DEBUG, "scales_per_type:")
    def _scales_per_type(self, worker_estimates_per_type):
        return [self._calc_scale(w) for w in worker_estimates_per_type]

    def _calc_scale(self, worker_type_estimate):
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
