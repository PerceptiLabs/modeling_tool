import warnings
import functools

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


def frontend_watcher(process_id, sleep_period=1, grace_period=15, log=None):
    """Monitor the existence of frontend process. If the monitored process does not exist, shut down

    For a discussion on the intricacies this topic:
    https://stackoverflow.com/questions/1489669/how-to-exit-the-entire-application-from-a-python-thread"""
    import os
    import time
    import psutil
    
    while True:
        if not psutil.pid_exists(process_id):
            if log:
                log.warning(
                    f"Frontend process [{process_id}] not found. "
                    f"This process will self terminate in {grace_period} seconds"
                )
            time.sleep(grace_period) # Give a grace period of N seconds before the process self terminates.

            if log:
                log.warning(f"Frontend process [{process_id}] not found. Terminating this process.")
            os.kill(os.getpid(), 9)

        time.sleep(sleep_period)


def sanitize_path(path):
    path = path.replace('\\', '/')
    return path

    
if __name__ == "__main__":
    import numpy as np
    obj = {
        'hello': '123456',
        'hehe': {
            'bla': [213,]*10,
            'zzz': np.random.random((25, 323))
        }
    }    
    x = stringify(obj)
    print(x)


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

