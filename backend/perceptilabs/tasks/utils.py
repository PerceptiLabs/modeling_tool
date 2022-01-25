import logging

import perceptilabs.settings as settings
from perceptilabs.utils import Timer
from perceptilabs.tasks.celery_executor import CeleryTaskExecutor
from perceptilabs.tasks.threaded_executor import ThreadedTaskExecutor


logger = logging.getLogger(__name__)



def get_task_executor():
    timers = {}

    
    def on_task_sent(task_id, task_name):
        timers[task_id] = Timer()
        timers[task_id].mark('sent')
        
        logger.info(f"Enqueued task '{task_name}' with ID {task_id}")        

    def on_task_received(task_id, task_name):
        if task_id in timers:
            timers[task_id].mark('received')
            
        logger.info(f"Worker received task '{task_name}' with ID {task_id}")

    def on_task_started(task_id):
        if task_id in timers:
            timers[task_id].mark('started')
            
        logger.info(f"Worker started task with ID {task_id}")

    def format_durations(task_id):
        if task_id in timers:
            timers[task_id].mark('finished')

            durations = timers[task_id].calc(
                t_until_queued=('sent', 'received'),
                t_in_queue=('received', 'started'),
                t_duration=('started', 'finished')
            )

            text = ""
            for key, value in durations.items():
                text += f"\n  {key}: {value:.3f}s"
                
            return text
        else:
            return ""

    def on_task_succeeded(task_id):
        logger.info(
            f"Worker succeeded with task with ID {task_id}" + format_durations(task_id))
 
    def on_task_failed(task_id):
        logger.info(
            f"Worker failed task with ID {task_id}" + format_durations(task_id))
    
    if settings.CELERY:
        return CeleryTaskExecutor(
            on_task_sent=on_task_sent,
            on_task_received=on_task_received,
            on_task_started=on_task_started,            
            on_task_succeeded=on_task_succeeded,
            on_task_failed=on_task_failed
        )
    else:
        return ThreadedTaskExecutor(
            on_task_sent=on_task_sent,
            on_task_received=on_task_received,
            on_task_started=on_task_started,            
            on_task_succeeded=on_task_succeeded,
            on_task_failed=on_task_failed
        )
