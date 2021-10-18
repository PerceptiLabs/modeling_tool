import base64
import pickle
import os
from perceptilabs.utils import sanitize_path


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
        padded_id = (training_session_id + '==').encode()  # TODO: should I just use model id for now instead of introducing a new concept!?

        #print("URL: http://localhost:5001/models/blabla/training/{}/status".format(training_session_id))
        
        directory = base64.urlsafe_b64decode(padded_id).decode()
        directory = sanitize_path(directory)  # For now, the ID is just the checkpoint dir

        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, 'latest-training-results.pkl')
        return file_path

