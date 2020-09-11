from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class ProcessReshapeSpec(InnerLayerSpec):
    type_: str = 'ProcessReshape'
    shape: Tuple[int, ...] = ()
    permutation: Tuple[int, ...] = ()
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['shape'] = tuple(dict_['Properties']['Shape'])
            params['permutation'] = tuple(dict_['Properties']['Permutation'])

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'Shape': self.shape,
            'Permutation': self.permutation
        }
        return dict_
