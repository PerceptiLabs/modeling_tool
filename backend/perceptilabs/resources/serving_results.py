import base64
import uuid
import pickle
import tempfile
import os
import shutil
import logging
from retrying import retry
from filelock import FileLock
from PIL import Image
from pathlib import Path

from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path


logger = logging.getLogger(__name__)


class ServingResultsAccess:
    FILE_NAME = 'latest-serving-results.pkl'

    def __init__(self, rygg):
        self._rygg = rygg

    def new_id(self, call_context, model_id):  # TODO: remove model id as an arg
        model_dir = self._rygg.get_model(call_context, model_id)['location']
        model_dir = model_dir.replace('\\', '/')  # Sanitize Windows path        
        serving_path = os.path.join(model_dir, 'serving', uuid.uuid4().hex)
        session_id = base64.urlsafe_b64encode(serving_path.encode()).decode()        
        return session_id
    
    def store(self, serving_session_id, results):
        if serving_session_id is None:
            return None

        directory = self.get_serving_directory(serving_session_id, allow_create=True)
        
        path = os.path.join(directory, self.FILE_NAME)
        logger.info(f"Resolved path to store results: {path}")
        
        with FileLock(path+'.lock'):
            with open(path, 'wb') as f:
                pickle.dump(results, f)

        logger.info(f"Wrote serving results to {path}")
                
    def get_latest(self, serving_session_id):
        directory = self.get_serving_directory(serving_session_id, allow_create=False)
        if directory is None:
            logger.info(f"No serving directory found for serving session {serving_session_id}")
            return None
            
        path = os.path.join(directory, self.FILE_NAME)
        logger.info(f"Resolved path to store results: {path}")

        if path is None or not os.path.isfile(path):
            logger.error(f"No serving results found at {path}")
            return None

        with FileLock(path+'.lock'):
            with open(path, 'rb') as f:
                results_dict = pickle.load(f)
                return results_dict

    def get_serving_directory(self, serving_session_id, allow_create=True):
        directory = b64decode_and_sanitize(serving_session_id)  # For now it's just a base64 path
        logger.info(
            f"Resolved serving directory {directory} for serving session {serving_session_id}")
        
        if allow_create:
            os.makedirs(directory, exist_ok=True)

        if os.path.isdir(directory):
            return directory
        else:
            return None

    def create_dir_for_gradio_examples(samples):
        examples = list()
        examples_path = 'gradio_examples'
        Path(examples_path).mkdir(parents=True, exist_ok=True)
        for index, path in enumerate(samples):
            im = Image.open(path)
            file_name = 'example_' + str(index) + '.jpg'
            full_path = Path(examples_path, file_name)
            try:
                im = im.save(full_path)
                examples.append([str(full_path)])
            except NotImplementedError: # If we run into write issues in docker, catch the exception and return 
                return
        
        return examples

    def remove_gradio_examples_dir():
        if Path.is_dir('gradio_examples'):
            Path.rmdir('gradio_examples')
            logger.info(f"Removed gradio examples directory")
            
    def remove(self, serving_session_id):
        directory = self.get_serving_directory(serving_session_id, allow_create=False)

        if os.path.isdir(directory):
            shutil.rmtree(directory)
            logger.info(f"Removed directory {directory} for session {serving_session_id}")

    def get_served_zip(self, serving_session_id, file_name='model.zip'):
        directory = self.get_serving_directory(serving_session_id)
        return os.path.join(directory, file_name)
