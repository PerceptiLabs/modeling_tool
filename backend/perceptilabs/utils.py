import os
import sys
import json
import bisect
import time
import copy
import warnings
import functools
from concurrent.futures import Future, Executor
from threading import Lock
import pkg_resources
import psutil


import numpy as np
import pandas as pd
from sys import getsizeof
from typing import Set



def get_memory_usage():
    """ Return the fraction of memory used """
    total_memory = psutil.virtual_memory().total # Deceptive naming (virtual memory), but OK according to docs: https://psutil.readthedocs.io/en/latest/
    available_memory = psutil.virtual_memory().available
        
    fraction_used = (total_memory-available_memory)/total_memory
    return fraction_used
    
    
def get_app_variables():
    with open(pkg_resources.resource_filename('perceptilabs', 'app_variables.json'), 'r') as f:
        app_variables = json.load(f)
    return app_variables


def get_version():
    from perceptilabs import __version__
    return __version__
    

def is_dev():
    return get_version() == "development"


def is_prod():
    return not is_dev()


def is_pytest():
    return "pytest" in sys.modules


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

def line_nums(text):
    lines = text.split('\n')
    max_numbering_length = len(str(len(lines) + 1))

    new_text = ''
    for line_no, line_txt in enumerate(lines):
        new_text += str(line_no + 1).rjust(max_numbering_length, ' ') + ' ' + line_txt + '\n'
    return new_text


add_line_numbering = lambda x: line_nums(x) # backwards compatibility


def dump_system_info(path):
    import multiprocessing
    import platform
    import time
    import json

    info = {}
    info['cpu_count'] = multiprocessing.cpu_count()
    info['time_zone'] = time.tzname
    
    info['platform'] = {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version()
    }

    with open(path, 'w') as f:
        json.dump(info, f, indent=4)

        
def dump_build_info(path):
    import json

    info = {}
    info['commit'] = ''
    info['version'] = ''    
    
    with open(path, 'w') as f:
        json.dump(info, f, indent=4)


def stringify(obj, max_len=70, new_lines=False, indent=0, sort=False):
    def _format(value):
        value_str = str(value)
        if not new_lines:
            value_str = value_str.replace('\n', '')            
        if len(value_str) > max_len:
            value_str = value_str[0:max_len] + '...'
        value_str = f'{value_str} [{type(value).__name__}]'            
        return value_str

    def search(obj, path=''):
        if type(obj) in [list, tuple, set]:
            nesting = any(type(x) in [list, tuple, set, dict] for x in obj)
            if nesting and len(str(obj).replace('\n', '')) > max_len:            
                for i, o in enumerate(obj):
                    search(o, path=f'{path}/{i}')
            else:
                val_str = _format(obj)                
                pairs.append((path+'/', val_str))
                
        elif isinstance(obj, dict):
            if len(str(obj).replace('\n', '')) > max_len:
                for k, o in obj.items():
                    search(o, path=f'{path}/{k}')
            else:
                val_str = _format(obj)
                pairs.append((path+'/', val_str))
        else:
            val_str = _format(obj)                            
            pairs.append((path, val_str))
            
    pairs = []
    search(obj)
    
    text = ''
    n_chars = max(len(p) for p, _ in pairs)

    if sort:
        pairs = sorted(pairs, key=lambda x: x[0])
    
    for path, value in pairs:
        text += ' '*indent + path.ljust(n_chars, ' ') + ' : ' + value + '\n'
                          
    return text


def frontend_watcher(process_id, sleep_period=1, grace_period=15, logger=None):
    """Monitor the existence of frontend process. If the monitored process does not exist, shut down

    For a discussion on the intricacies this topic:
    https://stackoverflow.com/questions/1489669/how-to-exit-the-entire-application-from-a-python-thread"""
    import os
    import time
    import psutil
    
    while True:
        if not psutil.pid_exists(process_id):
            if logger:
                logger.warning(
                    f"Frontend process [{process_id}] not found. "
                    f"This process will self terminate in {grace_period} seconds"
                )
            time.sleep(grace_period) # Give a grace period of N seconds before the process self terminates.

            if logger:
                logger.warning(f"Frontend process [{process_id}] not found. Terminating this process.")
            os.kill(os.getpid(), 9)

        time.sleep(sleep_period)


def sanitize_path(path):
    path = path.replace('\\', '/')
    return path


def loop_until_true(condition, timeout=20.0):
    import time
    t1 = t0 = time.time()
    while t1 - t0 < timeout:
        if condition(0):
            return True
        time.sleep(0.3)
        t1 = time.time()
    return False
        
    
def wait_for_condition(condition, timeout=20.0):
    return loop_until_true(condition, timeout)


def get_start_nodes(graph):
    start_nodes = []
    for id_, content in graph.items():
        if not content["backward_connections"]:
            start_nodes.append(id_)
        return start_nodes

    
@deprecated
def patch_net_connections(original_network):
    """ Converts forward/backward connection layers to comply with new standard """
    if True:
        return original_network
    

class DummyExecutor(Executor):

    def __init__(self):
        self._shutdown = False
        self._shutdownLock = Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdownLock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = Future()
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                f.set_exception(e)
            else:
                f.set_result(result)

            return f

    def shutdown(self, wait=True):
        with self._shutdownLock:
            self._shutdown = True

            
def get_object_size(data_obj, obj_ids: Set[int]) -> int:
    '''Recursively gets an objects total size in bytes
    
    Args:
        obj: Object to get total size of
    
    Returns:
        total_size: Size of object in bytes
    '''
    if data_obj is None:
        return 0
        
    if id(data_obj) in obj_ids:
        return 0

    obj_ids.add(id(data_obj))

    if isinstance(data_obj, (str, int, float, complex, bool)):
        data_obj_size = getsizeof(data_obj)
        return data_obj_size

    elif isinstance(data_obj, (list, set, range)):
        return 0
        #TODO: This crashes in Cython, fix before releasing data container
        # data_obj_size = getsizeof(data_obj)
        # return data_obj_size + sum([get_object_size(data, obj_ids) for data in data_obj])

    elif isinstance(data_obj, np.ndarray):
        return getsizeof(data_obj)

    elif isinstance(data_obj, pd.DataFrame):
        return data_obj.memory_usage(index=True, deep=True).sum()

    elif isinstance(data_obj, dict):
        data_obj_size = getsizeof(data_obj)
        return data_obj_size + sum([get_object_size(key, obj_ids) + get_object_size(val, obj_ids) for key, val in data_obj.items()])
    
    else:
        return 0



    
class RateCounter:
    
    class Entry:
        def __init__(self, t, v):
            self.t = t
            self.v = v
            
        def __lt__(self, other):
            return self.t < other.t            
    
    def __init__(self, window):
        self._window = window
        self._entries = []

    def _purge(self):
        i = 0
        t = time.time()
        while i < len(self._entries):
            if self._entries[i].t < t - self._window:
                del self._entries[i]
            i += 1
            
    def add_entry(self, value=None):
        bisect.insort(self._entries, self.Entry(time.time(), value or 1))

    def get_average_value(self):
        self._purge()
        try:
            return sum(e.v for e in self._entries)/self._window
        except:
            return 0

    def get_average_count(self):
        self._purge()
        try:
            return len(self._entries)/self._window
        except:
            return 0


def format_logs_zipfile_name(session_id, issue_id=None):
    import datetime

    time = datetime.datetime.utcnow()

    year = str(time.year).zfill(4)
    month = str(time.month).zfill(2)
    day = str(time.day).zfill(2)

    if issue_id is None:
        filename = f"default-{year}-{month}-{day}-{session_id}.txt"
    else:
        filename = f"issue-{issue_id}-{year}-{month}-{day}-{session_id}.txt"        

    return filename

    
def allow_memory_growth_on_gpus():
    """ Prevents crashes for unnecessary resource allocation """
    import tensorflow as tf
    gpu_devices = tf.config.list_physical_devices('GPU')
    for device in gpu_devices:
        tf.config.experimental.set_memory_growth(device, True)

    


    
        
        
            
if __name__ == "__main__":
    rc = RateCounter(1)
    import pdb; pdb.set_trace()
