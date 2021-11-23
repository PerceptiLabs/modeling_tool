import celery
from celery.result import AsyncResult
from threading import Event, Thread
from time import sleep

from rygg.celery import app as celery_app
from rygg.tasks.util import to_status_percent

def curry(fn, arg):
    def inner(*args, **kwargs):
        return fn(arg, *args, **kwargs)

    return inner


def is_running(task_id):
    as_dict = celery_app.control.inspect().active() or {}
    for worker_tasks in as_dict.values():
        for task in worker_tasks:
            if task['id'] == task_id:
                return True
    return False


# Returns a cancel_token
# and runs a thread that sets the token if it sees the cancel flag set in redis.
# Stops the thread when the task is no longer running
def start_canceler(task_id):
    cancel_token = Event()

    def is_canceled():
        with celery_app.backend.client as c:
            return c.exists(f"task_cancel:{task_id}") != 0

    def poll_for_cancellation():
        while not is_canceled() and not cancel_token.is_set() and is_running(task_id):
            #TODO: reset to 1 second
            sleep(0.1)

        cancel_token.set()

    Thread(target=poll_for_cancellation, daemon=True).start()
    return cancel_token


def work_in_celery(task, fn, *args, **kwargs):

    def update_status(expected, so_far, message):
        state = "STARTED"
        if expected == so_far:
            state = "SUCCESS"

        task.update_state(
            state=state,
            meta={
                'expected': expected,
                'so_far': so_far,
                'message': message,
            }
        )


    # wrap update_status with to_status_percent so that we emit percentages
    callback = curry(to_status_percent, update_status)

    task_id = task.request.id

    # start watching for the cancel flag
    cancel_token = start_canceler(task_id)

    try:
        # do the work
        fn(cancel_token, callback, *args, **kwargs)
    finally:
        # set the cancel_token for good measure
        cancel_token.set()


def enqueue_celery(task_name, *args, **kwargs):
    task = celery_app.tasks[task_name].delay(*args, **kwargs)
    celery_app.backend.store_result(task.id, {"message": f"Queued {task_name} task for {args}"}, "PENDING")
    return task.id


def get_celery_task_status(task_id):
    task = AsyncResult(task_id, app=celery_app)
    if task.info:
        if isinstance(task.info, Exception):
            return {"state": "FAILED"}

        return {"state": task.state, **task.info}
    elif task.successful():
        return {"state": "SUCCESS"}
    else:
        return None

def set_cancel_flag(task_id):
    with celery_app.backend.client as c:
        c.setex(f"task_cancel:{task_id}", 1800, "1")

def cancel_celery_task(task_id):
    # stop any workers from picking up the task
    celery_app.control.revoke(task_id)

    # Stop any running tasks
    set_cancel_flag(task_id)
