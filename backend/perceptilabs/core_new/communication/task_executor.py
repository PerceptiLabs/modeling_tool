import sys
import time
import queue
import threading


from perceptilabs.core_new.communication.utils import KillableThread

class TaskError(Exception):
    pass


class TaskTimeout(Exception):
    pass

        

class TaskExecutor:
    """ Killing threads works between atomic operations. E.g., killing during a time.sleep(20) will require 20 seconds"""    
    def __init__(self):
        self._task_queue = queue.Queue()
        self._result_queue = queue.Queue()

        self._stopped = threading.Event()
        self._worker_thread = KillableThread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def shutdown(self, kill=False):
        self._stopped.set()
        if kill:
            self._worker_thread.kill()
        else:
            self._worker_thread.join()

    def run(self, func, args=None, kwargs=None, timeout=None):
        if self._stopped.is_set():
            raise RuntimeError("Executor was stopped. Cannot run tasks!")
        
        self._task_queue.put(
            (func, args or (), kwargs or {})
        )
        try:
            value, exception = self._result_queue.get(timeout=timeout)
        except queue.Empty:
            self.shutdown(kill=True)
            raise TaskTimeout
        else:
            if exception is not None:
                raise TaskError from exception
            return value

    def _worker(self):
        while not self._stopped.is_set():
            try:
                func, args, kwargs = self._task_queue.get(timeout=1.0)
            except queue.Empty:
                pass
            else:
                self._process_task(func, args, kwargs)

    def _process_task(self, func, args, kwargs):
        try:
            result = func(*args, **kwargs)                
        except Exception as e:
            self._result_queue.put((None, e))                
        else:
            self._result_queue.put((result, None))
            
        
