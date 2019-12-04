import logging
from threading import Lock
from collections import namedtuple

CacheEntry = namedtuple('CacheEntry', ['inserting_layer', 'value'])

log = logging.getLogger(__name__)


def lock(func):
    def wrapper(self, *args, **kwargs):
        log.debug("Acquiring lock...")        
        self._lock.acquire()
        try:
            return func(self, *args, **kwargs)
        finally:
            log.debug("Releasing lock...")            
            self._lock.release()            
    return wrapper


class SessionCache:
    def __init__(self):
        self._lock = Lock()        
        self._dict = {}

    @lock
    def __contains__(self, key):
        return key in self._dict

    @lock
    def put(self, key, value, layer_id):
        if key in self._dict:
            message = "Overwriting cache entry {} ({}->{})".format(key, self._dict[key].value.__class__.__name__, value.__class__.__name__)
            log.warning(message)
        else:
            log.debug("Creating new cache entry {} [{}]".format(key, value.__class__.__name__))

        entry = CacheEntry(inserting_layer=layer_id, value=value)
        self._dict[key] = entry

    @lock        
    def get(self, key):
        if not key in self._dict:
            raise ValueError("No entry with key {} in cache!".format(key))

        entry = self._dict.get(key)
        log.debug("Loading entry {} [{}] from cache...".format(key, entry.value.__class__.__name__))
        return entry.value

    @lock    
    def invalidate(self, keep_layers):
        new_dict = {key: entry for key, entry in self._dict.items()
                    if entry.inserting_layer in set(keep_layers)}

        n_entries = len(self._dict.keys())        
        n_removed = n_entries - len(new_dict.keys())
        self._dict = new_dict
        log.info("Cache invalidation removed {}/{} entries".format(n_removed, n_entries))


_default_cache = SessionCache()

def get_cache():
    return _default_cache

        
if __name__ == "__main__":

    cache = SessionCache()
    cache.put('x', 123, 'layerid')

    print('x' in cache)
    
    import pdb; pdb.set_trace()
