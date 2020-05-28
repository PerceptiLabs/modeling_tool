import os
import json
import logging
import datetime
import pkg_resources
import jsonschema


import perceptilabs


APPLICATION_LOGGER = 'perceptilabs.applogger'
APPLICATION_LOG_FILE = 'kernel.log'
APPLICATION_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s'
APPLICATION_LOG_LEVEL = logging.INFO


DATA_LOGGER = 'perceptilabs.datalogger'
DATA_LOG_FILE = 'data.log'


def setup_application_logger():
    formatter = logging.Formatter(APPLICATION_LOG_FORMAT)
    
    file_handler = logging.FileHandler(APPLICATION_LOG_FILE, mode='w')
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()        
    stream_handler.setFormatter(formatter)
    
    logger = logging.getLogger(APPLICATION_LOGGER)
    logger.setLevel(APPLICATION_LOG_LEVEL)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


_global_context = {
    'session_id': '',
    'user_email': 'notset@perceptilabs.com'
}


def set_session_id(session_id):
    global _global_context
    _global_context['session_id'] = session_id

    
def set_user_email(email):
    global _global_context
    _global_context['user_email'] = email
    


class DataFormatter(logging.Formatter):
    def __init__(self):
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

        return text


def setup_data_logger():
    formatter = DataFormatter()
    
    file_handler = logging.FileHandler(DATA_LOG_FILE, mode='w')
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()        
    stream_handler.setFormatter(formatter)
    
    logger = logging.getLogger(DATA_LOGGER)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    #logger.addHandler(stream_handler)

    
def upload_logs(session_id):
    import os
    import time
    import uuid
    import shutil
    import tempfile

    logger = logging.getLogger(APPLICATION_LOGGER)

    from perceptilabs.azure import AzureUploader, AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU, AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US
    
    data_uploaders = [
        AzureUploader(AZURE_ACCOUNT_NAME_EU, AZURE_ACCOUNT_KEY_EU, AZURE_CONTAINER_EU),
        AzureUploader(AZURE_ACCOUNT_NAME_US, AZURE_ACCOUNT_KEY_US, AZURE_CONTAINER_US)        
    ]

    try:
        directory_path = tempfile.mkdtemp(prefix='perceptilabs_logs_')
        archives_path = tempfile.mkdtemp(prefix='perceptilabs_archives_')
        
        shutil.copy(APPLICATION_LOG_FILE, os.path.join(directory_path, APPLICATION_LOG_FILE))
        shutil.copy(DATA_LOG_FILE, os.path.join(directory_path, DATA_LOG_FILE))

        zip_name = "logs_{}_{}".format(int(time.time()), session_id)        
        zip_path_no_ext = os.path.join(archives_path, zip_name)
        zip_full_path = zip_path_no_ext + '.zip'

        shutil.make_archive(zip_path_no_ext, 'zip', root_dir=directory_path)
        shutil.copyfile(zip_full_path, 'bundle.zip') # TODO: only in debug mode??

        for uploader in data_uploaders:
            uploader.upload(zip_full_path)
            logger.info(f"Ran uploader {uploader}. File path: {zip_full_path}")        
    finally:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        if os.path.exists(archives_path):
            shutil.rmtree(archives_path)    

