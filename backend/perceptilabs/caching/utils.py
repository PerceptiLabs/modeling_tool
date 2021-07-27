import os
import redis
import pickle
import logging

from perceptilabs.caching.base import BaseCache
from perceptilabs.lwcore import LightweightCache    
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


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
    def __init__(self, password=None):
        self._conn = redis.Redis(
            'localhost',
            password=password,
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
    redis_password = os.getenv("PL_KERNEL_REDIS_PASSWORD", None)

    if redis_password is not None:
        logger.info("Using 'Redis' cache for pipeline metadata...")
        return RedisCache(password=redis_password)
    else:
        logger.info("Using 'Dict' cache for pipeline metadata...")        
        return DictCache()
    
def get_preview_cache():
    redis_password = os.getenv("PL_KERNEL_REDIS_PASSWORD", None)

    if redis_password is not None:
        logger.info("Using 'Redis' cache for previews...")
        return RedisCache(password=redis_password)
    else:
        logger.info("Using 'Lightweight' cache for previews...")        
        return LightweightCache(max_size=25)

    
def format_key(parameters):
    key = ':'.join(
        (p if p is not None else 'None')
        for p in parameters
    )
    return key
