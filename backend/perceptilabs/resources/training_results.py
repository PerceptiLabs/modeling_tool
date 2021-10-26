import base64
import pickle
import os
from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path
import time
import platform
class TrainingResultsAccess:
    def store(self, training_session_id, results):
        if training_session_id is None:
            return None

        path = self._get_path(training_session_id)
        with open(path, 'wb') as f:
            pickle.dump(results, f)            

    def get_latest(self, training_session_id):
        if training_session_id is None:
            return None

        path = self._get_path(training_session_id)
        if not os.path.isfile(path):
            return None
        
        with open(path, 'rb') as f:
            results_dict = pickle.load(f)
            return results_dict        

    def _get_path(self, training_session_id):
        directory = b64decode_and_sanitize(training_session_id)  # For now it's just a base64 path
        
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, 'latest-training-results.pkl')
        return file_path
        
    def remove(self, training_session_id):
        
        if training_session_id is not None:
            path = self._get_path(training_session_id)
            if os.path.isfile(path):
                while True:     #without this, deleting file operation breaks in windows os
                    try:
                        os.remove(path)
                        break
                    except:
                        continue
        

