from multiprocessing import Queue, Process

def _is_main_thread():
    from threading import current_thread, main_thread
    return current_thread().ident == main_thread().ident


def pass_through(q, fn, args, kwargs):
    try:
        ret = fn(*args, **kwargs)
        q.put(ret)
    except Exception as e:
        q.put(e)


def run_on_main_thread(fn, *args, **kwargs):
    if _is_main_thread():
        return fn(*args, **kwargs)

    q = Queue()
    p = Process(target=pass_through, args=(q, fn, args, kwargs))
    p.start()
    ret = q.get()
    p.join()
    return ret

