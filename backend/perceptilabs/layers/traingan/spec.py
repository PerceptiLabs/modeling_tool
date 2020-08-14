from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, LayerConnection
from perceptilabs.layers.specbase import sanitize_name
from perceptilabs.layers.utils import resolve_tf1x_stop_cond


class TrainGanSpec(LayerSpec):
    type_: str = 'TrainGan'
    batch_size: int = 8
    switch_layer_name: Union[str, None] = None
    real_layer_name: Union[str, None] = None
    n_epochs: int = 10
    generator_optimizer: str = 'tf.compat.v1.train.GradientDescentOptimizer'
    discriminator_optimizer: str = 'tf.compat.v1.train.GradientDescentOptimizer'
    learning_rate: float = 0.001    
    decay_rate: Union[float, None] = 0.96
    decay_steps: Union[int, None] = 100000
    momentum: Union[float, None] = 0.9
    beta1: Union[float, None] = 0.9
    beta2: Union[float, None] = 0.999
    stop_condition: str = 'Epochs'
    target_acc: Union[int, None] = None
    distributed: bool = False
    use_cpu: bool = False

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['batch_size'] = dict_['Properties']['batch_size']
            params['n_epochs'] = dict_['Properties']['Epochs']
            params['generator_optimizer'] = dict_['Properties']['Optimizer']
            params['discriminator_optimizer'] = dict_['Properties']['Optimizer']
            params['learning_rate'] = dict_['Properties']['Learning_rate']
            params['decay_steps'] = dict_['Properties']['Decay_steps']
            params['decay_rate'] = dict_['Properties']['Decay_rate']
            params['momentum'] = dict_['Properties']['Momentum']
            params['beta1'] = dict_['Properties']['Beta_1']
            params['beta2'] = dict_['Properties']['Beta_2']
            params['distributed'] = dict_['Properties'].get('Distributed', False)
            params['target_acc'] = dict_['Properties'].get('Stop_Target_Accuracy', None)
            params['stop_condition'] = dict_['Properties']['Stop_condition']    
            params['switch_layer_name'] = dict_['Properties']['switch_layer']
            params['real_layer_name'] = dict_['Properties']['real_data_layer']
            params['use_cpu'] = dict_['Properties'].get('Use_CPU', True)
        return cls(**params)
    
    def _to_dict_internal(self, dict_: Dict[str, Any]) -> Dict[str, Any]:
        """ Deconstructs a layer spec into a 'json network' layer dict """

        props = {
            'Learning_rate': self.learning_rate,
            'Decay_rate': self.decay_rate,
            'Decay_steps': self.decay_steps,
            'Momentum': self.momentum,
            'Beta_2': self.beta2,
            'Beta_1': self.beta1,
            'Optimizer': self.generator_optimizer,
            'Epochs': self.n_epochs,
            'batch_size': self.batch_size,
            'Use_CPU': self.use_cpu,
            'switch_layer': self.switch_layer_name,
            'Stop_condition': self.stop_condition,
            'Stop_Target_Accuracy': self.target_acc, 
            'real_data_layer': self.real_layer_name,
        }
        dict_['Properties'] = props        
        
        return dict_

