from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec


none_type = type(None)

class DeepLearningConvSpec(LayerSpec):
    _parameters = [
        ParamSpec('dropout', (float, none_type), None, 'The probability to keep a neuron dring training. If None, all neurons will be kept'),
        ParamSpec('conv_dim', (str,), '2D', 'The dimension of the convolution operation'),
        ParamSpec('patch_size', (int,), 3, ''),
        ParamSpec('feature_maps', (int,), 8, ''),
        ParamSpec('stride', (int, none_type), 2, ''),
        ParamSpec('padding', (str, none_type), 'SAME', ''),
        ParamSpec('activation', (str, none_type), 'Sigmoid', ''),
        ParamSpec('pooling', (str, none_type), None, ''),
        ParamSpec('pool_padding', (int, none_type), None, ''),
        ParamSpec('pool_area', (int, none_type), None, ''),
        ParamSpec('pool_stride', (int, none_type), None, ''),
    ]

    
class DeepLearningConvBuilder(LayerSpecBuilder):
    target_class = DeepLearningConvSpec

    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)

        if 'Properties' in dict_ and dict_['Properties'] is not None:        
            if dict_['Properties']['Dropout']:
                self.set_parameter('dropout', dict_['Properties']['Keep_prob'])
            else:
                self.set_parameter('dropout', None)            

            self.set_parameter('conv_dim', dict_['Properties']['Conv_dim'])
            self.set_parameter('patch_size', int(dict_['Properties']['Patch_size']))
            self.set_parameter('feature_maps', int(dict_['Properties']['Feature_maps']))
            self.set_parameter('stride', int(dict_['Properties']['Stride']))
            self.set_parameter('padding', dict_['Properties']['Padding'])
            self.set_parameter('activation', dict_['Properties']['Activation_function'])
            
            if dict_['Properties']['PoolBool']:
                self.set_parameter('pooling', dict_['Properties']['Pooling'])
                self.set_parameter('pool_padding', dict_['Properties']['Pool_padding'])
                self.set_parameter('pool_area', dict_['Properties']['Pool_area'])
                self.set_parameter('pool_stride', dict_['Properties']['Pool_stride'])

        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)

        props = {}
        
        props['Dropout'] = existing.dropout is not None
        props['Keep_prob'] = existing.dropout
        props['Conv_dim'] = existing.conv_dim
        props['Patch_size'] = existing.patch_size
        props['Feature_maps'] = existing.feature_maps
        props['Stride'] = existing.stride
        props['Padding'] = existing.padding
        props['Activation_function'] = existing.activation

        props['PoolBool'] = existing.pooling is not None
        props['Pooling'] = existing.pooling
        props['Pool_area'] = existing.pool_area
        props['Pool_padding'] = existing.pool_padding
        props['Pool_stride'] = existing.pool_stride

        dict_['Properties'] = props
        
        return dict_

