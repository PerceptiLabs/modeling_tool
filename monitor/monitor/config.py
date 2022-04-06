import os
from monitor.utils import dig
import yaml


class Config:
    def __init__(self, as_dict):
        self._inner = as_dict

    @property
    def as_dict(self):
        return self._inner

    @property
    def tasks(self):
        return [
            (tn, qn)
            for qn, qd in self._inner["queues"].items()
            for tn, v in qd["tasks"].items()
        ]

    @classmethod
    def load(cls):
        if not os.path.isfile("queues.yaml"):
            raise Exception("Didn't find queues.yaml.")

        with open("queues.yaml", "r") as f:
            as_dict = yaml.safe_load(f)

        return cls(as_dict)

    def for_task(self, queue_name, task_name):
        return dig(self._inner, "queues", queue_name, "tasks", task_name)

    def deployment_for_worker(self, worker_type):
        return dig(self._inner, "worker_types", worker_type, "deployment")
