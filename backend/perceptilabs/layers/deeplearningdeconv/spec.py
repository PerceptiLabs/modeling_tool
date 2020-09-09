from typing import Tuple, Dict, Any, Union, List

from perceptilabs.layers.specbase import LayerSpec
from perceptilabs.layers.utils import try_cast


class DeepLearningDeconvSpec(LayerSpec):
    type_: str = 'DeepLearningDeconv'
    batch_norm: bool = False
    dropout: bool = False
    keep_prob: float = 0.0
    deconv_dim: str = '2D'
    patch_size: int = 3
    feature_maps: int = 8
    stride: int = 2
    padding: str = 'SAME'
    activation: Union[str, None] = 'Sigmoid'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:        
            params['dropout'] = dict_['Properties']['Dropout']                
            params['keep_prob'] = try_cast(dict_['Properties']['Keep_prob'], float)
            params['batch_norm'] = try_cast(dict_['Properties'].get('Batch_norm'), bool)
            params['deconv_dim'] = str(dict_['Properties']['Deconv_dim'])
            params['patch_size'] = int(dict_['Properties']['Patch_size'])
            params['feature_maps'] = int(dict_['Properties']['Feature_maps'])
            params['stride'] = int(dict_['Properties']['Stride'])
            params['padding'] = dict_['Properties']['Padding']
            params['activation'] = dict_['Properties']['Activation_function']
            
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:            
        """ Deconstructs a layer spec into a 'json network' layer dict """
        props = {}
        
        props['Dropout'] = self.dropout
        props['Keep_prob'] = self.keep_prob
        props['Batch_norm'] = self.batch_norm
        props['Deconv_dim'] = self.deconv_dim
        props['Patch_size'] = self.patch_size
        props['Feature_maps'] = self.feature_maps
        props['Stride'] = self.stride
        props['Padding'] = self.padding
        props['Activation_function'] = self.activation

        dict_['Properties'] = props
        
        return dict_
