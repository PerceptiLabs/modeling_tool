from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec




class DeepLearningFcSpec(LayerSpec):
    _parameters = [
        ParamSpec('n_neurons', (int,), 10, 'The number of neurons'),
        ParamSpec('activation', (str,), 'Sigmoid', 'The activation function'),
        ParamSpec('dropout', (float, type(None),), None, 'The probability to keep a neuron dring training. If None, all neurons will be kept')
    ]
    
class DeepLearningFcBuilder(LayerSpecBuilder):
    target_class = DeepLearningFcSpec

    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)
        
        if 'Properties' in dict_ and dict_['Properties'] is not None:                        
            self.set_parameter('n_neurons', int(dict_['Properties']['Neurons']))
            self.set_parameter('activation', dict_['Properties']['Activation_function'])

            if dict_['Properties']['Dropout']:
                self.set_parameter('dropout', dict_['Properties']['Keep_prob'])
            else:
                self.set_parameter('dropout', None)
        return self

    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)
        
        props = {}
        props['Dropout'] = existing.dropout is not None
        props['Keep_prob'] = existing.dropout
        props['Neurons'] = existing.n_neurons
        props['Activation_function'] = existing.activation

        dict_['Properties'] = props
        return dict_
