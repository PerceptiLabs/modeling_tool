# Provides a lazy enumerator for when we know the size up front
class PresizedIterator:
    def __init__(self, expected_count, to_enumerate):
        self._expected_count = expected_count
        self._iter = iter(to_enumerate)
        self._done = 0

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iter)

    def __len__(self):
        return self._expected_count

    @property
    def progress(self):
        if self._expected_count == 0:
            return 100

        return (self._done / self._expected_count) * 100
