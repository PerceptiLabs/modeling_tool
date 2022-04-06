from celery import Celery
from monitor.log import logged_generator
from monitor.settings import REDIS_URL, CONFIG
from monitor.utils import dig, slice
from redis import Redis
import itertools
import json
import logging

TASK_ROUTES = {tn: {"queue": qn} for tn, qn in CONFIG.tasks}

celery_app = Celery("", broker=REDIS_URL, task_routes=TASK_ROUTES)


def active_tasks():
    # type: ignore
    tbl = celery_app.control.inspect().active() or {}
    for tasks in tbl.values():
        for task in tasks:
            yield {
                "queue": dig(task, "delivery_info", "routing_key"),
                **slice(task, "name", "id", "args", "kwargs"),
                "state": "ACTIVE",
            }


def reserved_tasks():
    tbl = celery_app.control.inspect().reserved() or {}
    for tasks in tbl.values():
        for task in tasks:
            yield {
                "queue": dig(task, "delivery_info", "routing_key"),
                **slice(task, "name", "id", "args", "kwargs"),
                "state": "RESERVED",
            }


def unsafe_iter_redis_list(key):
    r = Redis.from_url(REDIS_URL)
    # TODO don't just grab the whole queue w/o paging
    for i, as_str in enumerate(r.lrange(key, 0, -1)):
        as_dict = json.loads(as_str)
        headers = as_dict.get("headers", {})
        yield slice(headers, "task", "id", "argsrepr", "kwargsrepr", "properties")


def pending_tasks():
    r = Redis.from_url(REDIS_URL)
    tally = {}
    for q, t in CONFIG.tasks:
        for task in unsafe_iter_redis_list(q):
            yield {
                "queue": q,
                "id": task.get("id"),
                "name": task.get("task"),
                "args": task.get("argsrepr"),  # TODO: parse them
                "kwargs": task.get("kwargsrepr"),  # TODO: parse them
                "state": "PENDING",
            }


@logged_generator(logging.DEBUG, "all tasks:")
def all_tasks():
    return itertools.chain(active_tasks(), reserved_tasks(), pending_tasks())
