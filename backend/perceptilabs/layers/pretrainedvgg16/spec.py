from typing import Tuple, Dict, Any, Union, List
import tensorflow as tf
from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec

class PreTrainedVGG16Spec(InnerLayerSpec):
    type_: str = 'PreTrainedVGG16'
    include_top: bool = False
    trainable: bool = False
    classes: Union[int, str, None] = None
    pooling: Union[str, None] = None
    weights: Union[str, None] = 'imagenet'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:        
            params['include_top'] = dict_['Properties']['include_top']
            params['trainable'] = dict_['Properties']['trainable']
            params['classes'] = dict_['Properties']['classes']
            params['weights'] = dict_['Properties']['weights']
            
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:            
        """ Deconstructs a layer spec into a 'json network' layer dict """
        props = {}

        props['include_top'] = self.include_top
        props['trainable'] = self.trainable
        props['classes'] = self.classes
        props['weights'] = self.weights

        dict_['Properties'] = props
        
        return dict_
