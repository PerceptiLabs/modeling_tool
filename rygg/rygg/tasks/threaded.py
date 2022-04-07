from threading import Event, Thread
import uuid

from rygg.tasks.util import to_status_percent


class LocalTasks:
    tasks = {}

    def add(task_id, thread, cancel_token):
        LocalTasks.tasks[task_id] = {
            "thread": thread,
            "cancel_token": cancel_token,
            "info": {
                "state": "PENDING",
            },
        }
        return task_id

    def update_state(task_id, state=None, meta=None):
        record = LocalTasks.tasks[task_id]
        if state:
            record["info"]["state"] = state

        if meta:
            record["info"]["meta"] = meta

    def get(task_id):
        return LocalTasks.tasks[task_id]["info"]

    def cancel(task_id):
        token = LocalTasks.tasks[task_id]["cancel_token"]
        if token:
            token.set()

    def completed(task_id):
        entry = LocalTasks.tasks[task_id]
        entry["cancel_token"] = None
        info = entry["info"]
        info["state"] = "SUCCESS"

    def failed(task_id, exception=None):
        entry = LocalTasks.tasks[task_id]
        entry["cancel_token"] = None
        info = entry["info"]
        info["state"] = "FAILED"
        info["exception"] = str(exception)


def curry(fn, arg):
    def inner(*args, **kwargs):
        return fn(arg, *args, **kwargs)

    return inner


def work_in_thread(fn, *args, **kwargs):
    def update_status(expected, so_far, message, exception=None):
        if exception:
            state = "FAILED"
        elif expected == so_far:
            state = "SUCCESS"
        else:
            state = "STARTED"

        meta = {
            "expected": expected,
            "so_far": so_far,
            "message": message,
        }
        if exception:
            meta["exception"] = str(exception)

        LocalTasks.update_state(
            task_id,
            state=state,
            meta=meta,
        )

    cancel_token = Event()
    task_id = str(uuid.uuid4())
    callback = curry(to_status_percent, update_status)

    def go():
        try:
            fn(cancel_token, callback, *args, **kwargs)
            update_status(100, 100, "complete")
            LocalTasks.completed(task_id)
        except Exception as e:
            update_status(100, to_status_percent.total_percent, str(e), exception=e)
            LocalTasks.failed(task_id, exception=e)

    t = Thread(target=go)
    task_id = LocalTasks.add(task_id, t, cancel_token)
    t.daemon = True
    t.start()
    return task_id


def get_threaded_task_status(task_id):
    internal = LocalTasks.get(task_id)
    meta = internal.get("meta") or {}
    ret = {
        "state": internal.get("state"),
        **meta,
    }
    return ret
