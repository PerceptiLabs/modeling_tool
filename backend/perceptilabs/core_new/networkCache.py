import logging
from collections import namedtuple
import copy

CacheEntry = namedtuple('CacheEntry', ['hash', 'session', 'error'])

log = logging.getLogger(__name__)

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
                log.warning("Layer %s has no hash code and will be skipped in the caching for now"%str(con))
        return hash_

    def needs_update(self, id_, content):
        return self._dict[id_].hash != self._calculate_hash(id_, content)

    def update(self, id_, content, session, error):
        if id_ in self._dict:
            log.info("Updating layer " + str(id_))        
        hash_ = self._calculate_hash(id_, content)
        entry = CacheEntry(hash = hash_, session = session, error = error)
        self._dict[id_] = entry
        log.info("Cached layers: " + str(self._dict.keys()))

    
