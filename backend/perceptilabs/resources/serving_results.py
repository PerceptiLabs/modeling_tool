import base64
import pickle
import tempfile
import os
from filelock import FileLock

from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path


class ServingResultsAccess:
    FILE_NAME = 'latest-serving-results.pkl'

    def new_id(self):
        dirpath = tempfile.mkdtemp()
        session_id = base64.urlsafe_b64encode(dirpath.encode()).decode()
        return session_id    
    
    def store(self, serving_session_id, results):
        if serving_session_id is None:
            return None

        path = self._get_path(serving_session_id)
        with FileLock(path+'.lock'):
            with open(path, 'wb') as f:
                pickle.dump(results, f)

    def get_latest(self, serving_session_id):
        if serving_session_id is None:
            return None

        path = self._get_path(serving_session_id)
        if not os.path.isfile(path):
            return None
        
        with FileLock(path+'.lock'):
            with open(path, 'rb') as f:
                results_dict = pickle.load(f)
                return results_dict        

    def _get_path(self, testing_session_id):
        directory = b64decode_and_sanitize(testing_session_id)  # For now it's just a base64 path
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, self.FILE_NAME)
        return file_path

