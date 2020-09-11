from typing import Tuple, Dict, Any, Union


from perceptilabs.layers.specbase import InnerLayerSpec, LayerSpec


class DeepLearningFcSpec(InnerLayerSpec):
    type_: str = 'DeepLearningFC'
    n_neurons: Union[int, None] = 10
    activation: str = 'Sigmoid'
    batch_norm: bool = False
    dropout: bool = False
    keep_prob: float = 0.0

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:                        
            params['n_neurons'] = int(dict_['Properties']['Neurons']) if dict_['Properties']['Neurons'] else None
            params['activation'] = dict_['Properties']['Activation_function']
            params['batch_norm'] = dict_['Properties'].get('Batch_norm', False)
            params['dropout'] = dict_['Properties']['Dropout']
            params['keep_prob'] = dict_['Properties']['Keep_prob']
        
        return cls(**params)
    
    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """ Deconstructs a layer spec into a 'json network' layer dict """
        props = {}
        props['Dropout'] = self.dropout
        props['Keep_prob'] = self.keep_prob
        props['Neurons'] = self.n_neurons
        props['Activation_function'] = self.activation
        props['Batch_norm'] = self.batch_norm
                   
        dict_['Properties'] = props
        return dict_
                   
