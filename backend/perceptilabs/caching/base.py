from abc import ABC, abstractmethod


def _format_compound_key(parameters):
    key = ':'.join(
        (p if p is not None else 'None')
        for p in parameters
    )
    return key

class BaseCache(ABC):
    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def put(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    def get_or_calculate(self, key, calculate):

        if key is not None and key in self:
            return self.get(key), True

        result = calculate()

        if key is not None:
            self.put(key, result)

        return result, False

    def for_compound_keys(self, make_key=_format_compound_key):
        return CompoundCache(self, make_key)

class CompoundCache(BaseCache):
    def __init__(self, wrapped, make_key=_format_compound_key):
        self._wrapped = wrapped
        self._make_key = make_key

    def get(self, key):
        k = self._make_key(key)
        return self._wrapped.get(k)

    def put(self, key, value):
        k = self._make_key(key)
        self._wrapped.put(k, value)
        return k

    def __contains__(self, key):
        k = self._make_key(key)
        return k in self._wrapped

    def __len__(self):
        return self._wrapped.len()

    def make_key(self, key):
        return self._make_key(key)        
        
