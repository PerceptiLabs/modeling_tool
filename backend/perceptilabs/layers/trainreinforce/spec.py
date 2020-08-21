from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, LayerConnection
from perceptilabs.layers.utils import resolve_checkpoint_path


class TrainReinforceSpec(LayerSpec):
    type_: str = 'TrainReinforce'
    history_length: int = 1
    n_episodes: int = 10
    optimizer: str = 'SGD'
    learning_rate: float = 0.01
    distributed: bool = False
    batch_size: int = 8
    n_steps_max: int = 8
    update_frequency: int = 4
    initial_exploration: float = 0.9
    discount_factor: float = 0.99
    replay_memory_size: int = 300000
    final_exploration: float = 0.1
    final_exploration_frame: int = 500
    target_network_update_frequency: int = 100
    use_cpu: bool = False
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['learning_rate'] = float(dict_['Properties']['Learning_rate'])
            params['distributed'] = float(dict_['Properties'].get('Distributed', False))
            params['optimizer'] = str(dict_['Properties']['Optimizer'])
            params['batch_size'] = int(dict_['Properties']['Batch_size'])        
            params['n_steps_max'] = int(dict_['Properties']['Max_steps'])
            params['history_length'] = int(dict_['Properties']['History_length'])
            params['n_episodes'] = int(dict_['Properties']['Episodes'])    
            params['use_cpu'] = bool(dict_['Properties'].get('Use_CPU', True))
        return cls(**params)
    
    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """ Deconstructs a layer spec into a 'json network' layer dict """

        props = {
            'Learning_rate': self.learning_rate,
            'Distributed': self.distributed,
            'Optimizer': self.optimizer,
            'Episodes': self.n_episodes,
            'Batch_size': self.batch_size,
            'Max_steps': self.n_steps_max,
            'History_length': self.history_length,
            'Use_CPU': self.use_cpu
        }
        dict_['Properties'] = props        
        
        return dict_

