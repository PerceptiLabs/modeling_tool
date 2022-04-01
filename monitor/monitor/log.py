import logging
from monitor.settings import LOG_LEVEL

numeric_level = getattr(logging, LOG_LEVEL.upper())
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % loglevel)

logging.basicConfig(
    format="%(asctime)s -- %(levelname)s -- %(message)s", level=numeric_level
)


def slow_log(level, make_msg):
    if logging.getLogger().isEnabledFor(level):
        logging.log(level, make_msg())


def log_sequence(level, title, seq):
    if not logging.getLogger().isEnabledFor(level):
        return seq

    if isinstance(seq, dict):
        if seq:
            logging.log(level, title)
            for k, v in seq.items():
                logging.log(level, f"{k}: {v}")
        return seq

    ret = list(seq)
    if ret:
        logging.log(level, title)
        for x in ret:
            logging.log(level, x)
    return ret


def logged_generator(level, title):
    def decorate(func):
        def inner(*args, **kwargs):
            return log_sequence(level, title, func(*args, **kwargs))

        return inner

    return decorate


def logged(level, title):
    def decorate(func):
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            logging.log(level, f"{title}: {ret}")
            return ret

        return inner

    return decorate
