import ast
from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec


class DataRandomSpec(LayerSpec):
    type_: str = 'DataRandom'
    shape: Union[Tuple[int, ...], int] = (1, 5, 7, 4, 7)
    distribution: str = 'Normal'
    mean: float = 0.1
    stddev: float = 0.5
    minval: float = 0.1
    maxval: float = 3.4
    seed_training: int = 1111
    seed_validation: int = 1234
    seed_testing: int = 5678


    @classmethod
    def resolve_shape(cls, shape_str):
        shape = ast.literal_eval(shape_str)
        if isinstance(shape, int):
            shape = (shape, )
        return shape
    
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        params['shape'] = cls.resolve_shape(dict_['Properties']['shape'])
        params['distribution'] = dict_['Properties']['distribution']
        params['mean'] = dict_['Properties']['mean']
        params['stddev'] = dict_['Properties']['stddev']
        params['minval'] = dict_['Properties']['min']
        params['maxval'] = dict_['Properties']['max']
        params['seed_training'] = dict_['Properties'].get('Training_Seed', 1111)
        params['seed_testing'] = dict_['Properties'].get('Testing_Seed', 1234)
        params['seed_validation'] = dict_['Properties'].get('Validation_Seed', 5678)
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'shape': str(self.shape),
            'distribution': self.distribution,
            'mean': self.mean,
            'stddev': self.stddev,
            'min': self.minval,
            'max': self.maxval,
            'Training_Seed': self.seed_training,
            'Testing_Seed': self.seed_testing,
            'Validation_Seed': self.seed_validation
        }
        return dict_
