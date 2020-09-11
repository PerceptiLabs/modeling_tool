from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class ProcessRescaleSpec(InnerLayerSpec):
    type_: str = 'ProcessRescale'
    width: int = 25
    height: int = 25
    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['width'] = dict_['Properties']['width']
            params['height'] = dict_['Properties']['height']

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'width': self.width,
            'height': self.height
        }
        return dict_
