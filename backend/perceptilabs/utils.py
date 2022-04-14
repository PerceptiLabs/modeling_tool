import base64
import pathlib
import math
import psutil
import GPUtil
import os
import sys
import json
import socket
import bisect
import time
import copy
import warnings
import functools
from concurrent.futures import Future, Executor
from threading import Lock
import pkg_resources
from abc import ABC, abstractmethod
from contextlib import contextmanager, closing
import traceback

import numpy as np
import pandas as pd
from sys import getsizeof
from typing import Set, Any

import sentry_sdk


class KernelError(Exception):
    def __init__(self, message, details=""):
        self.message = message
        self.details = details

    def to_dict(self):
        return {"message": self.message, "details": self.details}

    @classmethod
    def from_exception(cls, exception, message=None):
        if isinstance(exception, cls):
            return exception

        if message is None:
            message = repr(exception)

        tb_obj = traceback.TracebackException(
            exception.__class__, exception, exception.__traceback__
        )
        return cls(message=message, details="".join(tb_obj.format()))


def get_memory_usage():
    """Return the fraction of memory used"""
    total_memory = (
        psutil.virtual_memory().total
    )  # Deceptive naming (virtual memory), but OK according to docs: https://psutil.readthedocs.io/en/latest/
    available_memory = psutil.virtual_memory().available

    fraction_used = (total_memory - available_memory) / total_memory
    return fraction_used


def convert(obj):
    """Converts datatypes which can't be jsonified to a type which can"""
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif np.iscomplexobj(obj):
        return abs(obj)
    elif isinstance(obj, pathlib.Path):
        return str(obj)
    else:
        return json.JSONEncoder.default(obj)


def get_app_variables():
    with open(
        pkg_resources.resource_filename("perceptilabs", "app_variables.json"), "r"
    ) as f:
        app_variables = json.load(f)
    return app_variables


def get_version():
    from perceptilabs import __version__

    return __version__


def is_azure_pipelines():
    return os.getenv(
        "TF_BUILD"
    )  # Set to true if being ran by a build task. See https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml


def is_docker():
    try:
        return os.path.isfile("/.dockerenv")
    except:
        return False


def is_dev():
    return get_version() == "development"


def is_debug():
    args = set(sys.argv)
    return "--debug" in args or "-d" in args


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
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def line_nums(text):
    lines = text.split("\n")
    max_numbering_length = len(str(len(lines) + 1))

    new_text = ""
    for line_no, line_txt in enumerate(lines):
        new_text += (
            str(line_no + 1).rjust(max_numbering_length, " ") + " " + line_txt + "\n"
        )
    return new_text


add_line_numbering = lambda x: line_nums(x)  # backwards compatibility


def is_windows():
    return os.name == "nt"


def dump_system_info(path):
    import multiprocessing
    import platform
    import time
    import json

    info = {}
    info["cpu_count"] = multiprocessing.cpu_count()
    info["time_zone"] = time.tzname

    info["platform"] = {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
    }

    with open(path, "w") as f:
        json.dump(info, f, indent=4)


def dump_build_info(path):
    import json

    info = {}
    info["commit"] = ""
    info["version"] = ""

    with open(path, "w") as f:
        json.dump(info, f, indent=4)


def stringify(obj, max_len=70, new_lines=False, indent=0, sort=False):
    def _format(value):
        value_str = str(value)
        if not new_lines:
            value_str = value_str.replace("\n", "")
        if len(value_str) > max_len:
            value_str = value_str[0:max_len] + "..."
        value_str = f"{value_str} [{type(value).__name__}]"
        return value_str

    def search(obj, path=""):
        if type(obj) in [list, tuple, set]:
            nesting = any(type(x) in [list, tuple, set, dict] for x in obj)
            if nesting and len(str(obj).replace("\n", "")) > max_len:
                for i, o in enumerate(obj):
                    search(o, path=f"{path}/{i}")
            else:
                val_str = _format(obj)
                pairs.append((path + "/", val_str))

        elif isinstance(obj, dict):
            if len(str(obj).replace("\n", "")) > max_len:
                for k, o in obj.items():
                    search(o, path=f"{path}/{k}")
            else:
                val_str = _format(obj)
                pairs.append((path + "/", val_str))
        else:
            val_str = _format(obj)
            pairs.append((path, val_str))

    pairs = []
    search(obj)

    text = ""
    n_chars = max(len(p) for p, _ in pairs)

    if sort:
        pairs = sorted(pairs, key=lambda x: x[0])

    for path, value in pairs:
        text += " " * indent + path.ljust(n_chars, " ") + " : " + value + "\n"

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
            time.sleep(
                grace_period
            )  # Give a grace period of N seconds before the process self terminates.

            if logger:
                logger.warning(
                    f"Frontend process [{process_id}] not found. Terminating this process."
                )
            os.kill(os.getpid(), 9)

        time.sleep(sleep_period)


def sanitize_path(path):
    path = path.replace("\\", "/")
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
    """Converts forward/backward connection layers to comply with new standard"""
    if True:
        return original_network


class DummyExecutor(Executor):
    def __init__(self):
        self._shutdown = False
        self._shutdownLock = Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdownLock:
            if self._shutdown:
                raise RuntimeError("cannot schedule new futures after shutdown")

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
    """Recursively gets an objects total size in bytes

    Args:
        obj: Object to get total size of

    Returns:
        total_size: Size of object in bytes
    """
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
        # TODO: This crashes in Cython, fix before releasing data container
        # data_obj_size = getsizeof(data_obj)
        # return data_obj_size + sum([get_object_size(data, obj_ids) for data in data_obj])

    elif isinstance(data_obj, np.ndarray):
        return getsizeof(data_obj)

    elif isinstance(data_obj, pd.DataFrame):
        return data_obj.memory_usage(index=True, deep=True).sum()

    elif isinstance(data_obj, dict):
        data_obj_size = getsizeof(data_obj)
        return data_obj_size + sum(
            [
                get_object_size(key, obj_ids) + get_object_size(val, obj_ids)
                for key, val in data_obj.items()
            ]
        )

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
            return sum(e.v for e in self._entries) / self._window
        except:
            return 0

    def get_average_count(self):
        self._purge()
        try:
            return len(self._entries) / self._window
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
    """Prevents crashes for unnecessary resource allocation"""
    import tensorflow as tf

    gpu_devices = tf.config.list_physical_devices("GPU")
    for device in gpu_devices:
        tf.config.experimental.set_memory_growth(device, True)


def disable_gpus():
    import tensorflow as tf

    tf.config.set_visible_devices([], "GPU")


# -------------------- PYDANTIC CYTHON WORKAROUND --------------------
#
# Cython doesn't yet play well with annotations (required for Pydantic).
# See https://github.com/cython/cython/issues/3776
#
# There is also an issue with Pydantic and Cython. See below.
#
# This workaround BREAKS type checking for the compiled version, so therefore
# this workaround should be removed as soon as these issues are fixed.


import pydantic.main
from pydantic import BaseModel, validator


class MyModelMetaclass(pydantic.main.ModelMetaclass):
    # Cython has not caught up with Python 3.7. So we have to create __annotations__ manually
    # for Pydantic to work.

    def __new__(mcs, name, bases, namespace, **kwargs):
        if "__annotations__" not in namespace:
            untouched_types = pydantic.main.UNTOUCHED_TYPES

            annotations = {}
            for var_name, value in namespace.items():
                if pydantic.main.is_valid_field(var_name) and not isinstance(
                    value, untouched_types
                ):
                    annotations[var_name] = Any

            namespace["__annotations__"] = annotations

        return super().__new__(mcs, name, bases, namespace, **kwargs)


def dummy_func():
    pass


class MyPydanticBaseModel(BaseModel, metaclass=MyModelMetaclass):
    # Pydantic does not know how to ignore Cython functions, so we have to configure that explicitly

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (type(dummy_func),)


# -------------------- END OF PYDANTIC CYTHON WORKAROUND --------------------


def random_exception(
    prob=0.5, message="Random error! Disable this method in production!!"
):
    import random

    if random.random() <= prob:
        raise RuntimeError(message)


class Timer:
    def __init__(self):
        self._times = {}

    def mark(self, name):
        self._times[name] = time.perf_counter()

    @contextmanager
    def wrap(self, name):
        self.mark("pre_" + name)
        yield
        self.mark("post_" + name)

    @property
    def raw(self):
        return self._times

    def calc(self, **kwargs):
        def t(k1, k2):
            v1 = self._times.get(k1)
            v2 = self._times.get(k2)
            if v1 is None or v2 is None:
                return None
            else:
                return v2 - v1

        return {key: t(*val) for key, val in kwargs.items()}


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def find_free_port_in_range(min_port, max_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = min_port
    while port <= max_port:
        try:
            sock.bind(("", port))
            sock.close()
            return port
        except OSError:
            port += 1
    raise IOError("no free ports")


def b64decode_and_sanitize(input_):
    padded = (input_ + "==").encode()
    decoded = base64.urlsafe_b64decode(padded).decode()
    sanitized = sanitize_path(decoded)
    return sanitized


def get_categories_from_postprocessing(postprocessing):
    if not hasattr(postprocessing, "n_categories"):
        return []

    num_categories = postprocessing.n_categories
    categories = postprocessing(np.eye(num_categories)).numpy()
    decoded_categories = list()

    def _categories_need_decoding():
        if isinstance(categories[-1], bytes):
            return True
        return False

    if _categories_need_decoding():
        for category in categories:
            decoded_categories.append(category.decode("utf-8"))

    if decoded_categories == []:
        decoded_categories = list(range(num_categories))
    return decoded_categories


def setup_sentry():
    import logging
    from sentry_sdk.integrations.logging import LoggingIntegration
    import perceptilabs.settings as settings

    logger = logging.getLogger(__name__)

    if is_pytest():
        return

    if is_prod() and not settings.SENTRY_ENABLED_PROD:
        return

    if is_dev() and not settings.SENTRY_ENABLED_DEV:
        return

    if is_prod():
        environment = settings.SENTRY_ENV_PROD
        release = get_version()
    else:
        environment = settings.SENTRY_ENV_DEV
        release = sentry_sdk.utils.get_default_release()

    integrations = [
        LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=None,  # Don't send logs as events. Instead, focus on unhandled errors and send handled errors manually
        )
    ]
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=integrations,
        environment=environment,
        release=release,
    )
    logger.info(
        f"Initialized sentry for environment '{environment}' and release '{release}'"
    )


def send_ex_to_sentry(ex, call_context):
    with _sentry_context(call_context):
        sentry_sdk.capture_exception(ex)


def send_message_to_sentry(message, call_context):
    with _sentry_context(call_context):
        sentry_sdk.capture_message(message)


@contextmanager
def _sentry_context(call_context):
    import sentry_sdk

    user_email = call_context.get("user_email")
    user_id = call_context.get("user_id")

    # if we received the email in the call_context (e.g. with Keycloak), then send that. Otherwise use the id
    if user_email:
        user = {"email": user_email}
    elif user_id:
        # Sentry filters out strings with "auth" or "|" in them, thinking that they're passwords.
        # Work around that by cleaning up the user_id
        user = {"id": user_id.lower().replace("auth0|", "a0:")}
    else:
        user = None

    with sentry_sdk.push_scope() as scope:
        if user:
            scope.set_user(user)

        for k, v in call_context.items():
            scope.set_extra(k, v)

        scope.set_extra("user_email", user_email)
        scope.set_extra("user_id", user_id)
        yield scope
        sentry_sdk.flush()


def directory_tree(path):
    if not os.path.isdir(path):
        raise ValueError(f"Path {path} is not a directory")

    found = []
    for path, dirs, files in os.walk(path):
        for d in dirs:
            found_path = os.path.join(path, d)

            if not found_path.endswith(os.path.sep):
                found_path += os.path.sep  # dirs should end with /

            found.append(found_path)

        for f in files:
            found.append(os.path.join(path, f))

    return found


def get_dataframe_type(dataset_settings):
    datatypes = []
    for feature_name, feature_dict in dataset_settings["featureSpecs"].items():
        datatypes.append(feature_dict["datatype"].lower())
    if set(datatypes) == set(["image", "category", "x1", "y1", "x2", "y2"]):
        return "ObjectDetection"
    else:
        return "other"
