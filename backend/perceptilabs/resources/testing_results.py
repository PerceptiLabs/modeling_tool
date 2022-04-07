import base64
import tempfile
import pickle
import os
from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path
from filelock import FileLock


class TestingResultsAccess:
    FILE_NAME = "latest-testing-results.pkl"

    def new_id(self):
        dirpath = tempfile.mkdtemp()
        testing_session_id = base64.urlsafe_b64encode(dirpath.encode()).decode()
        return testing_session_id

    def store(self, testing_session_id, results):
        if testing_session_id is None:
            return None

        path = self._get_path(testing_session_id)
        with FileLock(path + ".lock"):
            with open(path, "wb") as f:
                pickle.dump(results, f)

    def get_latest(self, testing_session_id):
        if testing_session_id is None:
            return None

        path = self._get_path(testing_session_id)
        if not os.path.isfile(path):
            return None
        with FileLock(path + ".lock"):
            with open(path, "rb") as f:
                results_dict = pickle.load(f)
                return results_dict

    def _get_path(self, testing_session_id):
        directory = b64decode_and_sanitize(
            testing_session_id
        )  # For now it's just a base64 path

        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, self.FILE_NAME).replace("\\", "/")
        return file_path
