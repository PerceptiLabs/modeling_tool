from threading import Event, Thread
import uuid

from rygg.tasks.util import observe_work

class LocalTasks():
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
        LocalTasks.tasks[task_id]["cancel_token"].set()

    def completed(task_id):
        entry = LocalTasks.tasks[task_id]
        entry["cancel_token"] = None
        info = entry["info"]
        info["state"] = "SUCCESS"


def work_in_thread(fn, *args, **kwargs):
    def update_status(expected, so_far, message):
        state = "STARTED"
        if expected == so_far:
            state = "SUCCESS"

        LocalTasks.update_state(
            task_id,
            state=state,
            meta={
                'expected': expected,
                'so_far': so_far,
                'message': message,
            }
        )

    cancel_token = Event()
    task_id = str(uuid.uuid4())

    def go():
        status_seq = fn(cancel_token, *args, **kwargs)
        observe_work(status_seq, update_status)
        LocalTasks.completed(task_id)

    t = Thread(target=go)
    task_id = LocalTasks.add(task_id, t, cancel_token)
    t.daemon = True
    t.start()
    return task_id

def get_threaded_task_status(task_id):
    internal = LocalTasks.get(task_id)
    meta = internal.get("meta") or {}
    return {
        "state": internal.get("state"),
        **meta,
    }
