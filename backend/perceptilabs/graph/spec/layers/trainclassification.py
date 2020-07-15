from typing import Tuple, Dict

from perceptilabs.graph.spec.layers import LayerSpec, LayerSpecBuilder, ParamSpec


class TrainClassificationSpec(LayerSpec):
    _parameters = [
        ParamSpec('distributed', (bool,), False, 'Whether the training will run in distributed or non-distributed mode'),
        ParamSpec('learning_rate', (float,), None, 'The learning rate'),
        ParamSpec('decay_rate', (float,), None, 'The decay rate. Only valid for the momentum optimizer'),
        ParamSpec('decay_steps', (int,), None, 'The number of decay steps. Only valid for the momentum optimizer'),
        ParamSpec('momentum', (float,), None, 'The momentum. Only valid for the momentum optimizer'),
        ParamSpec('beta_2', (float,), None, 'The beta 2 value. Only valid for the Adam optimizer'),
        ParamSpec('beta_1', (float,), None, 'The beta 1 value. Only valid for the Adam optimizer'),
        ParamSpec('optimizer', (str,), None, "One of 'SGD', 'Momentum', 'ADAM', 'adagrad', 'RMSprop'"),
        ParamSpec('n_epochs', (int,), None, 'The number of epochs'),
        ParamSpec('batch_size', (int,), None, 'The minibatch size'),        
        ParamSpec('loss_function', (str,), None, 'The loss function. One of ?'), # TODO: add a list of valid los'),
        ParamSpec('layer_true', (str,), None, 'The id of the layer that outputs the ground target value'),
        ParamSpec('layer_pred', (str,), None, 'The id of the layer that outputs the predictions')
    ]

class TrainClassificationBuilder(LayerSpecBuilder):
    target_class = TrainClassificationSpec
        
    def from_dict(self, id_: str, dict_: Dict):
        self.from_dict_base(id_, dict_)
        
        if 'Properties' in dict_ and dict_['Properties'] is not None:                                
            self.set_parameter('learning_rate', float(dict_['Properties']['Learning_rate']))        
            self.set_parameter('decay_rate', float(dict_['Properties']['Decay_rate']))
            self.set_parameter('decay_steps', int(dict_['Properties']['Decay_steps']))
            self.set_parameter('momentum', float(dict_['Properties']['Momentum']))
            self.set_parameter('beta_2', float(dict_['Properties']['Beta_2']))
            self.set_parameter('beta_1', float(dict_['Properties']['Beta_1']))
            self.set_parameter('optimizer', str(dict_['Properties']['Optimizer']))
            self.set_parameter('n_epochs', int(dict_['Properties']['Epochs']))
            self.set_parameter('batch_size', int(dict_['Properties']['Batch_size']))        
            self.set_parameter('loss_function', str(dict_['Properties']['Loss']))
            self.set_parameter('layer_true', str(dict_['Properties']['Labels']))
            self.set_parameter('distributed', False)        

            bw_cons = dict_['backward_connections']
            id1, _ = bw_cons[0] if len(bw_cons) >= 1 else (None, None)
            id2, _ = bw_cons[1] if len(bw_cons) >= 2 else (None, None)

            if id1 == dict_['Properties']['Labels']:
                self.set_parameter('layer_pred', id2)            
            else:
                self.set_parameter('layer_pred', id1)
                
        return self
    
    def to_dict(self, existing: LayerSpec) -> Dict:
        dict_ = self.to_dict_base(existing)

        props = {
            'Learning_rate': existing.learning_rate,
            'Decay_rate': existing.decay_rate,
            'Decay_steps': existing.decay_steps,
            'Momentum': existing.momentum,
            'Beta_2': existing.beta_2,
            'Beta_1': existing.beta_1,
            'Optimizer': existing.optimizer,
            'Epochs': existing.n_epochs,
            'Batch_size': existing.batch_size,
            'Loss': existing.loss_function,
            'Labels': existing.layer_true,
            'Class_weights': '1'
        }
        dict_['Properties'] = props        
        return dict_
