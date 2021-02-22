import os
import json
import logging
import datetime
import pkg_resources
import jsonschema
import tensorflow as tf
import platform
import re

import perceptilabs
from perceptilabs.utils import is_tf2x

APPLICATION_LOGGER = 'perceptilabs.applogger'
APPLICATION_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'kernel.log')
APPLICATION_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(package)s:%(lineno)d - %(message)s'
APPLICATION_LOG_LEVEL = logging.INFO

USER_LOGGER = 'perceptilabs.consolelogger'
USER_LOG_FORMAT = '%(asctime)s - %(message)s'
USER_LOG_LEVEL = logging.INFO

DATA_LOGGER = 'perceptilabs.datalogger'
DATA_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data.log')
DATA_LOGGER_MAX_LENGTH_DEV = 1500 # Only show the first N characters in dev console

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

def is_docker():
    try:
        return os.path.isfile("/.dockerenv")
    except:
        return False

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

    
_global_context = {
    'session_id': '',
    'user_email': 'notset@perceptilabs.com',
    'commit_id': '',
    'system': platform.system(),
    'tf2x': is_tf2x()
}


def set_session_id(session_id):
    global _global_context
    _global_context['session_id'] = session_id


def set_user_email(email):
    global _global_context
    _global_context['user_email'] = email

    
def set_commit_id(commit_id):
    global _global_context
    _global_context['commit_id'] = commit_id
    

class DataFormatter(logging.Formatter):
    def __init__(self, max_length=None): 
        self._max_length = max_length
        super().__init__()

        with open(pkg_resources.resource_filename('perceptilabs', 'dataschema/master.json'), 'r') as f:
            master_schema = json.load(f)

        schema_path = 'file:///{0}/'.format(pkg_resources.resource_filename('perceptilabs', 'dataschema').replace("\\", "/"))
        resolver = jsonschema.RefResolver(schema_path, None)
        self.validator = jsonschema.Draft7Validator(master_schema, resolver=resolver)

    def format(self, record):
        dict_ = {
            'time_event': datetime.datetime.utcnow().isoformat(),
            'session_id': _global_context.get('session_id', ''),
            'user_email': _global_context.get('user_email', 'dev@perceptilabs.com'),
            'version': perceptilabs.__version__,
            'commit': _global_context.get('commit_id', ''),
            'system': _global_context.get('system', ''),
            'tf2x': _global_context.get('tf2x', ''),            
            record.msg: record.namespace
        }

        try:
            self.validator.validate(dict_)
            text = json.dumps(dict_)
        except Exception as e:
            import pprint
            pprint.pprint(dict_)
            logging.getLogger(APPLICATION_LOGGER).exception(f'Data log formatter failed for event {record.msg}')
            text = ''

        if self._max_length is None:
            return text
        else:
            return f"{text[:self._max_length]} ... message truncated, only showing first {self._max_length} characters"


def setup_data_logger(is_dev=True):
    logger = logging.getLogger(DATA_LOGGER)
    logger.setLevel(logging.DEBUG)

    formatter = DataFormatter()

    if should_log_to_file():
        file_handler = logging.FileHandler(DATA_LOG_FILE, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if is_dev:
        dev_formatter = DataFormatter(max_length=DATA_LOGGER_MAX_LENGTH_DEV)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(dev_formatter)
        # logger.addHandler(stream_handler)
    else:
        from perceptilabs.azure import AzureHandler
        azure_handler = AzureHandler.get_default()
        azure_handler.setFormatter(formatter)        
        logger.addHandler(azure_handler)

        from perceptilabs.mixpanel_handler import MixPanelHandler        
        mixpanel_handler = MixPanelHandler()
        mixpanel_handler.setFormatter(formatter)
        logger.addHandler(mixpanel_handler)
        

def upload_logs(zip_name):
    import os
    import time
    import uuid
    import shutil
    import tempfile

    logger = logging.getLogger(APPLICATION_LOGGER)

    from perceptilabs.azure import AzureUploader, AZURE_CONNSTR_EU, AZURE_CONTAINER_EU, AZURE_CONNSTR_US, AZURE_CONTAINER_US

    data_uploaders = [
        AzureUploader(AZURE_CONNSTR_EU, AZURE_CONTAINER_EU),
        AzureUploader(AZURE_CONNSTR_US, AZURE_CONTAINER_US)
    ]

    try:
        directory_path = tempfile.mkdtemp(prefix='perceptilabs_logs_')
        archives_path = tempfile.mkdtemp(prefix='perceptilabs_archives_')

        def make_temp_copy(source_file, temp_dir):
            dest_file = os.path.join(temp_dir, os.path.basename(source_file))
            shutil.copy(source_file, dest_file)

        make_temp_copy(APPLICATION_LOG_FILE, directory_path)
        make_temp_copy(DATA_LOG_FILE, directory_path)        
        
        zip_path_no_ext = os.path.join(archives_path, zip_name)
        zip_full_path = zip_path_no_ext + '.zip'

        shutil.make_archive(zip_path_no_ext, 'zip', root_dir=directory_path)
        shutil.copyfile(zip_full_path, os.path.join(os.path.dirname(os.path.abspath(__file__)),'bundle.zip')) # TODO: only in debug mode??

        for uploader in data_uploaders:
            uploader.upload(zip_full_path)
            logger.info(f"Ran uploader {uploader}. File path: {zip_full_path}")
    finally:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        if os.path.exists(archives_path):
            shutil.rmtree(archives_path)

