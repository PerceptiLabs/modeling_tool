from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class MathSoftmaxSpec(InnerLayerSpec):
    type_: str = 'MathSoftmax'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = None
        return dict_
