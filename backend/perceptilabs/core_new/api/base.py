from typing import Any, Tuple
from enum import Enum
import dill

from perceptilabs.core_new.api.mapping import ByteMap, EventBus


class StateApi:
    def __init__(self, name, config):
        self._byte_map = ByteMap(
            config['state_api_name'],
            config['dealer_address'],
            config['subscriber_address'],
            config['push_address']
    )
    
    def set(self, key: str, value: Any) -> None:
        self._byte_map[key.encode()] = dill.dumps(value)
        
    def get(self, key: str) -> Any:
        value_bytes = self._byte_map.get(key.encode())
        return dill.loads(value_bytes)
        
    def remove(self, key: str) -> None:
        del self._byte_map[key.encode()]

    def start(self):
        self._byte_map.start()

    def stop(self):
        self._byte_map.stop()
'''
        
class LogApi:

    class Handler:
        # Should extend handler of standard logger

        self._event_bus = EventBus(
            event_bus_name,
            config['dealer_address'],
            config['subscriber_address'],
            config['push_address']
        )

        def start(self):
            self._client.start()
        
        def stop(self):
            self._client.stop()
    
    @classmethod
    def get_handler(cls, event_bus_name, config):
        return cls.Handler()
'''
    
class UiApi:
    def __init__(self, name, config):
        pass


class Api:
    def __init__(self, name, network_config):
        self._state = StateApi('state-' + name, network_config)
        #self._log = LogApi('log-' + name, network_config)
        self._ui = UiApi('ui-' + name, network_config)
            
    def start(self):
        self._state.start()
        self._log.start()
        self._ui.start()

    def stop(self):
        self._state.stop()
        self._log.stop()
        self._ui.stop()

    @property
    def state(self):
        return self._state
    
    @property
    def log(self):
        return self._log
    
    @property
    def ui(self):
        return self._ui
    
