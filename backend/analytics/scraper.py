import os
import time
import logging
import inspect
import functools
import threading
from queue import Queue
from typing import Any, Dict, List
from collections import namedtuple

from analytics.handlers import *

DEFAULT_HANDLERS = [
    CoreInitHandler(),
    CubeHandler(),
    CpuAndMemHandler(),
    SessionOnRenderHandler()
]

log = logging.getLogger(__name__)

class Scraper:
    PERSIST_INTERVAL = 10 # [s] how often the persist job runs

    def __init__(self, handlers: List[ScraperHandler]=None):
        self._handlers = handlers if handlers is None else DEFAULT_HANDLERS
        self._entry_queue = Queue()
        self._lock = None
        self._stop_event = None
        self._worker_thread = None        
        self._output_directory = '.'
        
    def submit(self, tag: str, values_dict: Dict[str, Any]):
        if not self.is_running:
            # log.warning("Ignoring scraper submission. Scraper is not running.")
            return

        log.debug("Submit called with tag '{}'".format(tag))
        
        meta_dict = {
            'tag': tag,
            'time': time.time(),
            'thread_id': threading.get_ident()
        }
        
        return self._submit(meta_dict, values_dict)

    def _submit(self, meta: Dict[str, Any], values: Dict[str, Any]):        
        count = 0
        for handler in self._handlers:
            if not (handler is not None and handler.is_applicable(meta, values)):
                continue
            
            entries = handler.apply(meta, values)

            for e in entries:
                self._entry_queue.put(e)
            count += len(entries)

        if count > 0:
            log.debug("Submit with tag '{}' queued {} new entries".format(meta['tag'], count))
            
    def monitor(self, tag: str):
        def actual_decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return_value = func(*args, **kwargs)
                
                arg_names = inspect.getargspec(func)[0]
                args_dict = {name: value for name, value in zip(arg_names, args)}
                args_dict.update(kwargs)
                self.submit(tag, args_dict)

                return return_value
            return wrapper
        return actual_decorator

    def _persist_queued_values(self):
        entries = []
        while not self._entry_queue.empty():
            entries.append(self._entry_queue.get())

        entrxies = sorted(entries, key=lambda x: x.file)

        for entry in entries:
            file_path = os.path.join(self._output_directory, entry.file)
            log.debug("Writing to file {}".format(file_path))

            try:
                self._lock.acquire()
                with open(file_path, 'a') as f:
                    f.write(entry.value + '\n')
            except:
                logging.exception("Exception writing to file")
            finally:
                self._lock.release()
            
        if len(entries) > 0:
            log.info("Persisted {} scraper entries".format(len(entries)))
        
    def start(self):
        msg = ", ".join([repr(x) for x in self._handlers])
        log.info("Starting scraper with handlers: {}".format(msg))
        
        self.stop()
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        def run():
            counter = 0            
            while not self._stop_event.is_set():
                if counter % int(self.PERSIST_INTERVAL) == 0:
                    self._persist_queued_values()
                time.sleep(1)
                counter += 1
                
        self._worker_thread = threading.Thread(target=run)
        self._worker_thread.start()

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()

            if self._worker_thread is not None:
                log.debug("Joining worker thread...")
                self._worker_thread.join()
                
    def set_output_directory(self, path: str):
        self._output_directory = path

    @property
    def is_running(self):
        return self._stop_event is not None and not self._stop_event.is_set()
    
    
_default_scraper = Scraper(DEFAULT_HANDLERS)


def get_scraper():
    return _default_scraper


def submit(tag: str, time: float, args: Dict[str, Any], kwargs: Dict[str, Any]):
    return _default_scraper.submit(tag, time, args, kwargs)


def monitor(tag: str):
    return _default_scraper.monitor(tag)


def start():
    _default_scraper.start()

    
def stop():
    _default_scraper.stop()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.DEBUG)

    start()

    time.sleep(3)
    
    @monitor(tag='square')
    def square(x):
        print("squaring")
        return x**2

    @monitor(tag='cube')
    def cube(x):
        return x**3



    x = square(3)
    print('res from square', x)
    
    x = cube(3)
    print('res from cube', x)




    time.sleep(5.1)
    stop()    
    print(" stop!")
    
    
    #print("thread")
    #threading.Thread(target=square, args=(4,)).start()

    #print("proc")
    #import multiprocessing
    #multiprocessing.Process(target=cube, args=(5,)).start()
