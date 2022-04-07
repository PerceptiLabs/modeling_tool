class PreprocessingResultsAccess:
    def __init__(self, cache):
        self._cache = cache

    def set_results(self, session_id, status, metadata=None, error=None):
        self._cache.put(
            session_id, {"metadata": metadata, "status": status, "error": error}
        )

    def get_results(self, session_id):
        if session_id in self._cache:
            return self._cache.get(session_id)
        else:
            return None

    def get_status(self, session_id):
        results = self.get_results(session_id)
        if results:
            return results["status"]
        else:
            return None

    def get_metadata(self, session_id):
        results = self.get_results(session_id)
        if results:
            return results["metadata"]
        else:
            return None
