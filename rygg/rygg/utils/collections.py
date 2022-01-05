from typing import TypeVar, Generic

T = TypeVar('T')

# Provides a lazy enumerator for when we know the size up front
class PresizedIterator(Generic[T]):
    def __init__(self, expected_count: int, to_enumerate: Generic[T]):
        self._expected_count = expected_count
        self._iter = iter(to_enumerate)
        self._done = 0

    def __iter__(self) -> Generic[T]:
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def __len__(self) -> int:
        return self._expected_count

    @property
    def progress(self) -> float:
        if self._expected_count == 0:
            return 100

        return (self._done / self._expected_count) * 100

