from time import sleep
import os
from more_itertools import nth, consume
import re
from threading import Event, Thread

class OperationCancelledException(Exception):
    pass

def run_and_terminate(cancel_token, *args, **popen_kwargs):
    from subprocess import Popen, PIPE, CalledProcessError
    kwargs = {
        "bufsize": 1, # 1 = line-by-line
        "stdout": PIPE,
        "universal_newlines": True,
        **popen_kwargs
    }
    with Popen(*args, **kwargs) as p:
        try:
            for line in p.stdout:
                if cancel_token.is_set():
                    raise OperationCancelledException()

                yield line
        finally:
            p.terminate()

        p.wait(timeout=15)
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, p.args)


class SubprocessStatus():
    def __init__(self, expected):
        self._expected = expected
        self._count = 0
        self._done = False
        self._message = "Starting"
        self._error = None


    def incr(self, message):
        self._count += 1
        self._message = message


    def cancel(self):
        self._token.set()


    def done(self):
        self._done = True
        self._count = self._expected
        self._message = "Completed"


    @property
    def is_done(self):
        self.check()
        return self._done

    @property
    def expected(self):
        return self._expected

    @property
    def count(self):
        return self._count

    @property
    def message(self):
        self.check()

        return self._message

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, e):
        self._error = e


    def check(self):
        if self._error:
            raise self._error

class Unzipper():
    def __init__(self, zipfile, dest):
        if not os.path.isfile(zipfile):
            raise Exception(f"{zipfile} doesn't exist")

        self._zipfile = zipfile
        self._dest = dest


    def _check_version(self, cancel_token):
        SUPPORTED_VERSION="6.00"

        lines = run_and_terminate(cancel_token, ["unzip", "-v"])
        first_line = nth(lines, 0, default="")
        ok = first_line.startswith(f"UnZip {SUPPORTED_VERSION}")
        if not ok:
            raise Exception(f"Wrong version of unzip. Expected {SUPPORTED_VERSION}. Got version string '{first_line}'")


    def _get_expected(self, cancel_token):
        self._check_version(cancel_token)

        lines = run_and_terminate(cancel_token, ["unzip", "-Z", "-h", self._zipfile])
        second_line = nth(lines, 1, default="")
        pattern = r'Zip file size: .* bytes, number of entries: (?P<count>\d*)'
        m = re.match(pattern, second_line)
        expected_count = int(m.group("count"))
        return SubprocessStatus(expected_count)


    def _start_unzip(self, cancel_token):
        IS_CONTENT = lambda line: not line.startswith("-")
        HEADER_LINE_COUNT=1

        lines = run_and_terminate(cancel_token, ["unzip", "-o", self._zipfile, "-d", self._dest])

        # skip header
        consume(lines, HEADER_LINE_COUNT)

        return lines


    def _coalesce_output_to_status(self, status, lines):
        def watch_output(lines):
            try:
                for line in lines:
                    status.incr(line)

                status.done()
            except Exception as e:
                status.error = e

        thread = Thread(target=watch_output, args=(lines,))
        thread.start()


    def run(self, cancel_token, update_status_fn, update_interval=1):
        # Get expected contents of zipfile
        status = self._get_expected(cancel_token)

        # unzip and watch the output
        output = self._start_unzip(cancel_token)
        self._coalesce_output_to_status(status, output)

        while not status.is_done:
            update_status_fn(status.expected, status.count, status.message)
            sleep(update_interval)
        update_status_fn(status.expected, status.count, status.message)


if __name__ == "__main__":
    cancel_token = Event()
    from debug_print import _d
    def update_status(expected, count, message):
        _d(expected)
        _d(count)
        _d(message)
        # cancel_token.set()

    unzipper = Unzipper("/Users/j/Downloads/x/mnist_data.zip", "/Users/j/f/unziptoy/lala")
    cancel_token = unzipper.run(cancel_token, update_status)

