from typing import Tuple, Dict, Any

from perceptilabs.layers.specbase import LayerSpec


class DeepLearningRecurrentSpec(LayerSpec):
    type_: str = 'DeepLearningRecurrent'
    n_neurons: int = 10
    version: str = 'RNN'
    time_steps: int = 1
    return_sequence: bool = False
    activation: str = 'Sigmoid'
    dropout: bool = False
    keep_prob: float = 0.0

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:                        
            params['n_neurons'] = int(dict_['Properties']['Neurons'])
            params['version'] = dict_['Properties']['Version']
            params['time_steps'] = int(dict_['Properties']['Time_steps'])
            params['return_sequence'] = int(dict_['Properties']['Return_sequence'])
            params['activation'] = dict_['Properties']['Activation_function'] if dict_['Properties']['Activation_function'] else 'None'
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
        props['Version'] = self.version
        props['Time_steps'] = self.time_steps
        props['Return_sequence'] = self.return_sequence        
                   
        dict_['Properties'] = props
        return dict_
                   
