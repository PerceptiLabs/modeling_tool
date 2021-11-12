from multiprocessing import Queue, Process
from six import reraise
from tblib import pickling_support
pickling_support.install()
import pickle
import sys

def _is_main_thread():
    from threading import current_thread, main_thread
    return current_thread().ident == main_thread().ident


def pass_through(q, fn, args, kwargs):
    try:
        ret = fn(*args, **kwargs)
        rc = 0
    except:
        ret = sys.exc_info()
        rc = 1

    q.put(pickle.dumps(ret))
    exit(rc)

def run_on_main_thread(fn, *args, **kwargs):
    if _is_main_thread():
        return fn(*args, **kwargs)

    q = Queue()
    p = Process(target=pass_through, args=(q, fn, args, kwargs))
    p.start()
    p.join()

    pickled = q.get()
    ret = pickle.loads(pickled)
    if p.exitcode != 0:
        if hasattr(ret, "__iter__"):
            reraise(*ret)
        else:
            raise Exception(f"Internal Error: expected an exception but received {type(ret)}.")
    return ret

