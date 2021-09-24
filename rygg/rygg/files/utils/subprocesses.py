from subprocess import Popen, PIPE, CalledProcessError

class CanceledError(Exception):
    pass

def run_and_terminate(cancel_token, *args, **popen_kwargs):
    kwargs = {
        "bufsize": 1, # 1 = line-by-line
        "stdout": PIPE,
        "universal_newlines": True,
        **popen_kwargs
    }
    with Popen(*args, **kwargs) as p:
        try:
            for line in p.stdout:
                if cancel_token and cancel_token.is_set():
                    raise CanceledError()

                yield line
        finally:
            p.terminate()

        p.wait(timeout=15)
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, p.args)

def cancelable_sequence(seq, cancel_token):
    for x in seq:
        if cancel_token.is_set():
            raise CanceledError

        yield x

