from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class ProcessReshapeSpec(InnerLayerSpec):
    type_: str = 'ProcessReshape'
    shape: Tuple[int, ...] = ()
    permutation: Tuple[int, ...] = ()

    def get_permutation(self, indexing='zero'):
        """ Get significant values and possibly shift """
        new_permutation = self._get_significant_values(self.permutation)
        new_permutation = self._maybe_shift_permutation(new_permutation, indexing=indexing)
        return new_permutation

    def get_shape(self):
        """ Get shape without zeros/nones """
        new_shape = self._get_significant_values(self.shape)
        return new_shape

    def _maybe_shift_permutation(self, permutation, indexing):
        """ Whether to use zero-indexing or one-indexing """        
        if indexing == 'one':
            return tuple(x + 1 for x in permutation)
        else:
            return permutation        

    def _get_significant_values(self, original_values):
        """ Get values that correspond to a non-zero/non-none shape dimension """
        significant_values = [
            original_values[idx]
            for idx, dim in enumerate(self.shape)
            if dim is not None and dim != 0
        ]
        return tuple(significant_values)            
    
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
