# Extracted from https://github.com/pnpnpn/timeout-decorator since the upstream doesn't support windows
"""
Timeout decorator.

    :copyright: (c) 2012-2013 by PN.
    :license: MIT, see LICENSE for more details.
"""

import sys
import signal
from functools import wraps

IS_WIN = sys.platform.startswith("win")

############################################################
# Timeout
############################################################

# http://www.saltycrane.com/blog/2010/04/using-python-timeout-decorator-uploading-s3/
# Used work of Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>
# in https://code.google.com/p/verse-quiz/source/browse/trunk/timeout.py


class TimeoutError(AssertionError):

    """Thrown when a timeout occurs in the `timeout` context manager."""

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


def _raise_exception(exception, exception_message=None):
    """ This function checks if a exception message is given.

    If there is no exception message, the default behaviour is maintained.
    If there is an exception message, the message is passed to the exception with the 'value' keyword.
    """
    if exception_message is None:
        raise exception()
    else:
        raise exception(exception_message)


def timeout(seconds=None, timeout_exception=TimeoutError, exception_message=None):
    """Add a timeout parameter to a function and return it.

    :param seconds: optional time limit in seconds or fractions of a second. If None is passed, no timeout is applied.
        This adds some flexibility to the usage: you can disable timing out depending on the settings.
    :type seconds: float

    :raises: TimeoutError if time limit is reached

    It is illegal to pass anything other than a function as the first
    parameter. The function is wrapped and returned to the caller.
    """
    def decorate(function):

        if IS_WIN:
            return function

        def handler(signum, frame):
            _raise_exception(timeout_exception, exception_message=exception_message)

        @wraps(function)
        def new_function(*args, **kwargs):
            new_seconds = kwargs.pop('timeout', seconds)
            if new_seconds:
                old = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, new_seconds)

            if not seconds:
                return function(*args, **kwargs)

            try:
                return function(*args, **kwargs)
            finally:
                if new_seconds:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)
        return new_function

    return decorate

