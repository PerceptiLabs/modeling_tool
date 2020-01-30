def dump_system_info(path):
    import multiprocessing
    import platform
    import time
    import json

    info = {}
    info['cpu_count'] = multiprocessing.cpu_count()
    info['time_zone'] = time.tzname
    
    info['platform'] = {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version()
    }

    with open(path, 'w') as f:
        json.dump(info, f, indent=4)

        
def dump_build_info(path):
    import json

    info = {}
    info['commit'] = ''
    info['version'] = ''    
    
    with open(path, 'w') as f:
        json.dump(info, f, indent=4)


from collections import MutableMapping
import logging
import inspect

log = logging.getLogger(__name__)

class DictWrapper(MutableMapping):
    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __contains__(self, key):
        return key in self.store

    def __getitem__(self, key):
        if key not in self.store:
            caller = inspect.getframeinfo(inspect.stack()[2][0])
            log.debug(f"Dict '{self.tag}'.__getitem__ called with non-existing key '{key}'. Called from {caller.filename}:{caller.lineno}")
                    
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value
        
    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
        
