import logging
from collections import namedtuple
import copy
import gc

from perceptilabs.logconf import APPLICATION_LOGGER

CacheEntry = namedtuple('CacheEntry', ['hash', 'session', 'error'])

logger = logging.getLogger(APPLICATION_LOGGER)



class NetworkCache():
    def __init__(self):
        self._dict=dict()

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        return self._dict[key]

    def get_layers(self):
        return self._dict.keys()

    def remove_layer(self, id_):
        del self._dict[id_]
        gc.collect()

    def to_dict(self):
        return self._dict

    def _clean_content(self, content):
        clean_content = copy.deepcopy(content)
        try:
            del clean_content["Info"]["forward_connections"]
        except:
            pass
        return clean_content

    def _calculate_hash(self, id_, content):
        content = self._clean_content(content)

        hash_ = hash(str(content))
        for con in content["Con"]:
            if con in self._dict:
                hash_+=self._dict[con].hash
            else:
                logger.warning("Layer %s has no hash code and will be skipped in the caching for now"%str(con))
        return hash_

    def needs_update(self, id_, content):
        return self._dict[id_].hash != self._calculate_hash(id_, content)

    def update(self, id_, content, session, error):
        if id_ in self._dict:
            logger.info("Updating layer " + str(id_))  
            self.remove_layer(id_)       
        hash_ = self._calculate_hash(id_, content)
        entry = CacheEntry(hash = hash_, session = session, error = error)
        self._dict[id_] = entry
        logger.info("Cached layers: " + str(self._dict.keys()))

    
