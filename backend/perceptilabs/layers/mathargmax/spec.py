from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class MathArgmaxSpec(InnerLayerSpec):
    type_: str = 'MathArgmax'
    dimension: int = -1
    
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:                                
            params['dimension'] = int(dict_['Properties']['Dim'])
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {'Dim': self.dimension}
        return dict_
