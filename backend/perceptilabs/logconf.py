import os
import json
import logging
import datetime
import pkg_resources
import tensorflow as tf
import platform
import re

import perceptilabs
from perceptilabs.utils import is_docker

APPLICATION_LOGGER = 'perceptilabs.applogger'
APPLICATION_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'kernel.log')
APPLICATION_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(package)s:%(lineno)d - %(message)s'
APPLICATION_LOG_LEVEL = logging.INFO

USER_LOGGER = 'perceptilabs.consolelogger'
USER_LOG_FORMAT = '%(asctime)s - %(message)s'
USER_LOG_LEVEL = logging.INFO

class PackageFilter(logging.Filter):
    def filter(self, record):
        plabs_path = pkg_resources.resource_filename('perceptilabs', '')

        if record.pathname.startswith(plabs_path) and record.pathname.endswith('.py'):
            package_name = 'perceptilabs' + record.pathname[len(plabs_path):-3].replace('/', '.')
            record.package = package_name
        else:
            record.package = record.filename
            
        return True    

class QueueHandler(logging.Handler):
    """Handler object for adding logs from logger to the given queue.

    Args:
        message_queue (queue): queue to put the logs in. 
        *args, **kwargs: extra arguments to pass to the logging.Handler
    """
    def __init__(self, *args, message_queue, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.message_queue = message_queue
        self.previous_message = None

    def emit(self, record):
        message = self.prepare(record)
        if message is None:
            pass
        elif self.previous_message is not None and message[8:] == self.previous_message[8:]:
            pass
        else:
            self.message_queue.put(message)
            self.previous_message = message

    def prepare(self, record):
        message = self.format(record).rstrip('\n')
        # checking for tensorflow logs
        if 'From' in message: 
            result = re.search(r'From(.*?):\d+:', message)
            if result:
                position = result.span()
                string = message[position[0]:position[1]]
                log = message.replace(string,'')
        else:
            log = message
        return log


def is_podman():
    # see https://github.com/containers/podman/issues/3586
    # in podman, the "container" variable is set
    return os.getenv("container") is not None

def should_log_to_file():
    return not (is_docker() or is_podman())

def setup_application_logger(log_level=None):
    if log_level is not None:
        log_level = logging.getLevelName(log_level)
    
    logger = logging.getLogger(APPLICATION_LOGGER)
    logger.setLevel(log_level or APPLICATION_LOG_LEVEL)

    formatter = logging.Formatter(APPLICATION_LOG_FORMAT)

    if should_log_to_file():
        file_handler = logging.FileHandler(APPLICATION_LOG_FILE, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addFilter(PackageFilter())


def setup_general_logger(queue, log_level = None):
    """can be used if we want to send tensor logs to general tab.
        adding logs from tensorflow logger to general warnings handler.

    Args:
        queue (queue.Queue): queue to send the logs to.
        log_level (log_level, optional): Log level used for filtering logs. Defaults to None.
    """
    
    general_log_handler = QueueHandler(message_queue=queue, level=logging.INFO)
    general_log_formatter = logging.Formatter(USER_LOG_FORMAT,"%H:%M:%S")
    general_log_handler.setFormatter(general_log_formatter)
    
    tf_logger = tf.get_logger() 
    tf_logger.addHandler(general_log_handler)
    
def setup_console_logger(queue, log_level = None):
    """sets up the handlers for loggers so that logs can be shown in the console logs tab. 
        Also creates, a logger USER_LOGGER to easily send logs to console logs. 
        Logs of level warning and above from application_logger will also be sent to console logs.
    Args:
        queue (queue.Queue): queue to send the logs to.
        log_level (log_level, optional): Log level used for filtering logs. Defaults to None.
    """
    if log_level is not None:
        log_level = logging.getLevelName(log_level)
    
    user_logger = logging.getLogger(USER_LOGGER)
    user_logger.setLevel(log_level or USER_LOG_LEVEL)
    user_log_handler = QueueHandler(message_queue=queue, level=USER_LOG_LEVEL)
    user_log_formatter = logging.Formatter(USER_LOG_FORMAT,"%H:%M:%S")
    user_log_handler.setFormatter(user_log_formatter)
    user_logger.addHandler(user_log_handler)
    
    tf_logger = tf.get_logger() 
    tf_logger.addHandler(user_log_handler)

    # adding warning level logs from application logger to console log handler
    application_logger = logging.getLogger(APPLICATION_LOGGER)
    application_log_handler = QueueHandler(message_queue=queue, level=logging.WARNING)
    application_log_formatter = logging.Formatter(USER_LOG_FORMAT,"%H:%M:%S")
    application_log_handler.setFormatter(application_log_formatter)
    application_logger.addHandler(application_log_handler)

    
