from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec


class ProcessGrayscaleSpec(LayerSpec):
    type_: str = 'ProcessGrayscale'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        return dict_
