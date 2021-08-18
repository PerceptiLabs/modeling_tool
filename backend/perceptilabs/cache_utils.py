import os
import redis
import pickle
import logging
from abc import ABC, abstractmethod

from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
import perceptilabs.settings as settings

logger = logging.getLogger(APPLICATION_LOGGER)


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


class DictCache(BaseCache):
    def __init__(self):
        self._dict = dict()

    def get(self, key):
        return self._dict.get(key)

    def put(self, key, value):
        self._dict[key] = value

    def __setitem__(self, key, value):
        self.put(key, value)
    
    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._dict)


class RedisCache(BaseCache):
    def __init__(self):
        self._conn = redis.Redis(
            'localhost',
            port=6379,
            db=0
        )

    def get(self, key):
        data = self._conn.get(key)

        if data is not None:
            value = pickle.loads(data)
            return value
        else:
            return None

    def put(self, key, value):
        data = pickle.dumps(value)
        self._conn.set(key, data)

    def __setitem__(self, key, value):
        self.put(key, value)
    
    def __contains__(self, key):
        return bool(self._conn.exists(key))

    def __len__(self):
        return self._conn.dbsize()

    
def get_data_metadata_cache():
    redis_url = settings.REDIS_URL

    if redis_url is not None:
        logger.info("Using 'Redis' cache for pipeline metadata...")
        return RedisCache()
    else:
        logger.info("Using 'Dict' cache for pipeline metadata...")        
        return DictCache()
    
    
def format_key(parameters):
    key = ':'.join(
        (p if p is not None else 'None')
        for p in parameters
    )
    return key
