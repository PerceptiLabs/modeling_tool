from typing import Tuple, Dict, Any, Union

from perceptilabs.layers.specbase import LayerSpec, LayerConnection


class TrainRegressionSpec(LayerSpec):
    type_: str = 'TrainRegression'
    distributed: bool = False
    use_cpu: bool = False
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
    connection_labels: Union[LayerConnection, None] = None
    connection_predictions: Union[LayerConnection, None] = None                            

    @classmethod
    def _from_dict_internal(cls, id_: str, dict_: Dict[str, Any], params: Dict[str, Any]) -> LayerSpec:
        if 'Properties' in dict_ and dict_['Properties'] is not None:
            params['learning_rate'] = float(dict_['Properties']['Learning_rate'])        
            params['decay_rate'] = float(dict_['Properties']['Decay_rate'])
            params['decay_steps'] = int(dict_['Properties']['Decay_steps'])
            params['momentum'] = float(dict_['Properties']['Momentum'])
            params['beta2'] = float(dict_['Properties']['Beta_2'])
            params['beta1'] = float(dict_['Properties']['Beta_1'])
            params['optimizer'] = str(dict_['Properties']['Optimizer'])
            params['n_epochs'] = int(dict_['Properties']['Epochs'])
            params['batch_size'] = int(dict_['Properties'].get('Batch_size', 8))        
            params['class_weights'] = str(dict_['Properties']['Class_weights'])          
            params['distributed'] = False
            params['use_cpu'] = dict_['Properties'].get('Use_CPU', True)

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
            'Labels': self.connection_labels.src_id if self.connection_labels is not None else None,
            'Class_weights': self.class_weights,
            'Use_CPU': self.use_cpu,
        }
        dict_['Properties'] = props        
        
        return dict_

