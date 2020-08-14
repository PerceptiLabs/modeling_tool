from typing import Tuple, Dict, Any


from perceptilabs.layers.specbase import LayerSpec


class DeepLearningFcSpec(LayerSpec):
    type_: str = 'DeepLearningFC'
    n_neurons: int = 10
    activation: str = 'Sigmoid'
    batch_norm: bool = False
    dropout: bool = False
    keep_prob: float = 0.0

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:                        
            params['n_neurons'] = int(dict_['Properties']['Neurons'])
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
                   
