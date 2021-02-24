from typing import Dict, Any
from perceptilabs.layers.specbase import IoLayerSpec, LayerSpec


class InputLayerSpec(IoLayerSpec):
    type_: str = 'IoInput'
    datatype: str = ''
    feature_name: str = ''
    file_path: str = '' 


    @property
    def is_input_layer(self):
        return True

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['feature_name'] = dict_['Properties']['FeatureName']
            params['file_path'] = dict_['Properties']['FilePath']
            params['datatype'] = dict_['Properties']['DataType']                        

        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        dict_['Properties'] = {
            'FeatureName': self.feature_name,
            'FilePath': self.file_path,
            'DataType': self.datatype
        }
        return dict_
