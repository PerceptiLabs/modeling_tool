from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class MathMergeSpec(InnerLayerSpec):
    type_: str = 'MathMerge'
    merge_type: Union[str, None] = None
    merge_dim: Union[int, None] = None    

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        params['merge_type'] = dict_['Properties']['Type']
        merge_dim = dict_['Properties']['Merge_dim'] 
        params['merge_dim'] = int(merge_dim) if merge_dim != '' else None
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {}
        dict_['Properties']['Type'] = self.merge_type
        dict_['Properties']['Merge_dim'] = str(self.merge_dim)
        dict_['Properties']['Merge_order'] = None
        return dict_
