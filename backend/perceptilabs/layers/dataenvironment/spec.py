from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec


class DataEnvironmentSpec(LayerSpec):
    type_: str = 'DataEnvironment'
    environment_name: str = 'Breakout-v0'
    use_unity: bool = False
    unity_env_path: Union[None, str] = None # This should take a path to a UnityEnv in yaml format
    timeout_wait: float = 30.0

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        params['environment_name'] = dict_['Properties']['accessProperties']['Atari'] + '-v0'
        params['use_unity'] = dict_['Properties']['use_unity'] if 'use_unity' in dict_['Properties'] else False
        params['unity_env_path'] = dict_['Properties']['unity_env_path'] if 'unity_env_path' in dict_['Properties'] else None
        params['timeout_wait'] = dict_['Properties']['timeout_wait'] if 'timeout_wait' in dict_['Properties'] else 30.0
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'accessProperties': {'Atari': self.environment_name[:-3]}, # Drop last 3 chars "breakout-v0"
            'use_unity': self.use_unity,
            'unity_env': self.unity_env_path,
            'timeout_wait': self.timeout_wait
        } 
        return dict_
