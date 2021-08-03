from typing import Tuple, Dict, Any, Union, List
import tensorflow as tf
from perceptilabs.layers.specbase import LayerSpec, InnerLayerSpec


class UNetSpec(InnerLayerSpec):
    type_: str = 'UNet'
    filter_num: tuple = (64, 128, 256, 512)
    n_labels: int = 1
    stack_num_down: int = 2
    stack_num_up: int = 2
    activation: Union[str] = 'ReLU'
    output_activation: Union[None, str] = 'Softmax'
    batch_norm: bool = False
    pool: Union[bool, str] = 'max'
    unpool: Union[bool, str] = 'bilinear'
    backbone: Union[bool, str] = None
    backbone_weights: Union[bool, None, str] = 'imagenet'
    freeze_backbone: bool = False
    freeze_batch_norm: bool = False
    attention: bool = False
    atten_type: Union[str] = 'add'
    atten_activation: Union[str] = 'ReLU'
    name = 'UNet'

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            # params['filter_num'] = dict_['Properties']['filter_num'] #TODO: need to add at a later date
            params['n_labels'] = dict_['Properties']['n_labels']
            params['stack_num_down'] = dict_['Properties']['stack_num_down']
            params['stack_num_up'] = dict_['Properties']['stack_num_up']
            params['activation'] = dict_['Properties']['activation']
            params['output_activation'] = dict_['Properties']['output_activation']
            params['batch_norm'] = dict_['Properties']['batch_norm']
            params['pool'] = dict_['Properties']['pool']
            params['unpool'] = dict_['Properties']['unpool']
            params['backbone'] = dict_['Properties']['backbone']
            params['backbone_weights'] = dict_['Properties']['backbone_weights']
            params['freeze_backbone'] = dict_['Properties']['freeze_backbone']
            params['freeze_batch_norm'] = dict_['Properties']['freeze_batch_norm']
            params['attention'] = dict_['Properties']['attention']
            params['atten_type'] = dict_['Properties']['atten_type']
            params['atten_activation'] = dict_['Properties']['atten_activation']
        return cls(**params)

    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """ Deconstructs a layer spec into a 'json network' layer dict """
        props = {}

        # props['filter_num'] = self.filter_num
        props['n_labels'] = self.n_labels
        props['stack_num_down'] = self.stack_num_down
        props['stack_num_up'] = self.stack_num_up
        props['activation'] = self.activation
        props['output_activation'] = self.output_activation
        props['batch_norm'] = self.batch_norm
        props['pool'] = self.pool
        props['unpool'] = self.unpool
        props['backbone'] = self.backbone
        props['backbone_weights'] = self.backbone_weights
        props['freeze_backbone'] = self.freeze_backbone
        props['freeze_batch_norm'] = self.freeze_batch_norm
        props['attention'] = self.attention
        props['atten_type'] = self.atten_type
        props['atten_activation'] = self.atten_activation

        dict_['Properties'] = props

        return dict_
