from abc import ABC, abstractmethod


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
