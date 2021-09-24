from celery.decorators import task
from celery.result import AsyncResult
from threading import Event

from rygg.celery import app as celery_app
from rygg.tasks.util import observe_work

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

    # TODO: get canceled events from celery to pass on through the cancel token
    cancel_token = Event()
    status_seq = fn(cancel_token, *args, **kwargs)
    observe_work(status_seq, update_status)

def enqueue_celery(task_name, *args, **kwargs):
    task = celery_app.tasks[task_name].delay(*args, **kwargs)
    celery_app.backend.store_result(task.id, {"message": f"Queued {task_name} task for {args}"}, "PENDING")
    return task.id

def get_celery_task_status(task_id):
    task = AsyncResult(task_id, app=celery_app)
    if task.info:
        if isinstance(task.info, Exception):
            return {"state": "failed"}

        return {"state": task.state, **task.info}
    elif task.successful():
        return {"state": "SUCCESS"}
    else:
        return None

