from typing import Dict, Any
from perceptilabs.layers.specbase import IoLayerSpec, LayerSpec


class OutputLayerSpec(IoLayerSpec):
    type_: str = 'IoOutput'
    datatype: str = ''
    feature_name: str = ''
    file_path: str = '' # TODO: Remove. Also ask for frontend to remove this. 

    @property
    def is_target_layer(self):
        return True

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['feature_name'] = dict_['Properties']['FeatureName']
            params['datatype'] = dict_['Properties']['DataType']
            
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'FeatureName': self.feature_name,
            'DataType': self.datatype            
        }
        return dict_
