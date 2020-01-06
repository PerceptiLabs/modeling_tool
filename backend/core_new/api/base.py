from typing import Any, Tuple
import dill

from core_new.api.mapping import ByteMap


class StateApi:
    def __init__(self, config):
        self._byte_map = ByteMap(
            config['name'],
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

        
class LogApi:
    pass


class Api:
    def __init__(
            self,
            state_config: Dict[str, str, str, str]
    ):
        self._state = StateApi(state_config)
        
    def start(self):
        self._state.start()

    def stop(self):
        self._state.stop()

    @property
    def state(self):
        return self._state
    
