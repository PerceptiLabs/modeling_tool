
import base64
import time
import platform
import pickle
import os
import logging

from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path

from filelock import FileLock


logger = logging.getLogger(__name__)


class TrainingResultsAccess:
    FILE_NAME = 'latest-training-results.pkl'

    def __init__(self, rygg):
        self._rygg = rygg

    def store(self, training_session_id, results):
        if training_session_id is None:
            return None
            
        path = self._get_path(training_session_id)
        with FileLock(path+'.lock'):
            with open(path, 'wb') as f:
                pickle.dump(results, f)
                size = os.path.getsize(path)
                logger.info(f"Size of latest training results in bytes: {size}")

    def get_latest(self, training_session_id):
        if training_session_id is None:
            return None

        path = self._get_path(training_session_id)
        if not os.path.isfile(path):
            logger.error(f"Invalid training results path: {path} for training session id {training_session_id}")
            return None

        results_dict = {}
        with FileLock(path+'.lock'):
            with open(path, 'rb') as f:
                results_dict = pickle.load(f)

        if not results_dict:
            logger.error(f"Invalid training results for training session id {training_session_id}. No content found.")
            return None
        
        return results_dict        

    def _get_path(self, training_session_id):
        directory = self._rygg.get_model(training_session_id)['location']
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, self.FILE_NAME).replace('\\', '/')
        return file_path
        
    def remove(self, training_session_id):
        
        if training_session_id is not None:
            path = self._get_path(training_session_id)
            if os.path.isfile(path):
                with FileLock(path+'.lock'):
                    while True:     #without this, deleting file operation breaks in windows os
                        try:
                            os.remove(path)
                            break
                        except:
                            continue
        

