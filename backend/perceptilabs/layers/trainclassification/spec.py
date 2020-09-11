from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, LayerConnection, InnerLayerSpec


class TrainClassificationSpec(InnerLayerSpec):
    type_: str = 'TrainNormal'
    distributed: bool = False
    use_cpu: bool = True
    learning_rate: float = 0.01
    decay_rate: Union[float, None] = None
    decay_steps: Union[int, None] = None
    momentum: Union[float, None] = None
    beta1: Union[float, None] = None
    beta2: Union[float, None] = None
    optimizer: str = 'SGD'
    class_weights: Union[float, None] = None
    n_epochs: int = 10
    batch_size: int = 8
    loss_function: str = 'Quadratic'
    connection_labels: Union[LayerConnection, None] = None
    connection_predictions: Union[LayerConnection, None] = None    
    target_acc: Union[int, None] = None
    stop_condition: str = 'Epochs'                        

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['learning_rate'] = dict_['Properties']['Learning_rate']        
            params['decay_rate'] = dict_['Properties']['Decay_rate']
            params['decay_steps'] = dict_['Properties']['Decay_steps']
            params['momentum'] = dict_['Properties']['Momentum']
            params['beta2'] = dict_['Properties']['Beta_2']
            params['beta1'] = dict_['Properties']['Beta_1']
            params['optimizer'] = dict_['Properties']['Optimizer']
            params['n_epochs'] = dict_['Properties']['Epochs']
            params['batch_size'] = dict_['Properties']['Batch_size']
            params['class_weights'] = dict_['Properties']['Class_weights']
            params['loss_function'] = dict_['Properties']['Loss']
            params['distributed'] = False
            params['use_cpu'] = dict_['Properties'].get('Use_CPU', True)
            params['target_acc'] = dict_['Properties'].get('Stop_Target_Accuracy', None)
            params['stop_condition'] = dict_['Properties'].get('Stop_condition', None)

            conn_specs = dict_['backward_connections']
            for idx, conn_spec in enumerate(conn_specs):
                if conn_spec['dst_var'] == 'predictions':
                    params['connection_predictions'] = LayerConnection(
                        src_id=conn_specs[idx]['src_id'], src_var=conn_specs[idx]['src_var'],
                        dst_id=id_, dst_var=conn_specs[idx]['dst_var']
                    )                        
                    
                if conn_spec['dst_var'] == 'labels':
                    params['connection_labels'] = LayerConnection(
                        src_id=conn_specs[idx]['src_id'], src_var=conn_specs[idx]['src_var'],
                        dst_id=id_, dst_var=conn_specs[idx]['dst_var']
                    )
                    
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
            'Optimizer': self.optimizer,
            'Epochs': self.n_epochs,
            'Batch_size': self.batch_size,
            'Loss': self.loss_function,
            'Labels': self.connection_labels.src_id if self.connection_labels is not None else None,
            'Class_weights': self.class_weights,
            'Use_CPU': self.use_cpu,
            'Stop_Target_Accuracy': self.target_acc,
            'Stop_condition': self.stop_condition,
        }
        dict_['Properties'] = props        
        
        return dict_

