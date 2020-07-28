import logging
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


def resolve_tf1x_activation_name(specs):
    table = {
        None: None,
        '': None,
        'Sigmoid': 'tf.compat.v1.sigmoid',
        'ReLU': 'tf.compat.v1.nn.relu',
        'LeakyReLU': 'tf.compat.v1.nn.leaky_relu',
        'Softmax': 'tf.compat.v1.nn.softmax',
        'Tanh': 'tf.compat.v1.tanh'
    }

    activation = specs['Properties']['Activation_function']
    func_name = table.get(activation)
    if activation not in table:
        layer_id = '<not implemented>'
        logger.warning(f"layer {layer_id} specified activation {activation}, but it was not found in tf1x activations table. No activation will be used for this layer")

    return func_name

def resolve_tf1x_optimizer(specs):
    table = {
        'SGD': 'tf.compat.v1.train.GradientDescentOptimizer',
        'Momentum': 'tf.compat.v1.train.MomentumOptimizer',
        'ADAM': 'tf.compat.v1.train.AdamOptimizer',
        'adagrad': 'tf.compat.v1.train.AdagradOptimizer',
        'RMSprop': 'tf.compat.v1.train.RMSPropOptimizer',                       
    }

    optimizer = specs['Properties']['Optimizer']
    optimizer_class = table.get(optimizer)
    if optimizer not in table:
        raise NotImplementedError(f"Optimizer {optimizer} is not yet implemented")        

    return optimizer_class

def resolve_tf1x_stop_cond(specs):
    table = ["Epochs", "TargetAccuracy"]

    stop_cond = specs['Properties']['Stop_condition']
    if stop_cond not in table:
        raise NotImplementedError(f"Stop condition {stop_cond} is not yet implemented")


    stop_condition = [x for x in table if x == stop_cond][0]
    
    return stop_condition