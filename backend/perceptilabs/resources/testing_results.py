import base64
import tempfile

from perceptilabs.utils import b64decode_and_sanitize
from perceptilabs.utils import sanitize_path
from perceptilabs.caching.utils import get_test_results_cache


class TestingResultsAccess:
    FILE_NAME = "latest-testing-results.pkl"

    def __init__(self):
        self.results_cache = get_test_results_cache()

    def new_id(self):
        dirpath = tempfile.mkdtemp()
        testing_session_id = base64.urlsafe_b64encode(dirpath.encode()).decode()
        return testing_session_id

    def store(self, testing_session_id, results):
        if testing_session_id is None:
            return None

        self.results_cache.put(testing_session_id, results)

    def get_latest(self, testing_session_id):
        if testing_session_id is None:
            return None

        results_dict = self.results_cache.get(testing_session_id)
        return results_dict
