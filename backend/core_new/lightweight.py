import numpy as np
import tensorflow as tf

from core_new.core import BaseCore

def placeholder_hook_1(func, globals_, locals_, dtype, shape=None, name=None):    
    if shape is None:
        raise ValueError("Can only handle defined shapes in eager_mode!")

    matrix = np.zeros((1,)+tuple(shape[1:]))    
    const = tf.constant(matrix, dtype=tf.float32)
    #const = tf.constant(locals_['sample'])
    return const

def placeholder_hook_2(func, globals_, locals_, dtype, shape=None, name=None):
    if shape is None:
        raise ValueError("Can only handle defined shapes in eager_mode!")

    matrix = None
    for value in locals_.values():
        if not isinstance(value, np.ndarray):
            continue

        if len(value.shape) == len(shape) and value.shape[1:] == shape[1:]:
            matrix = value[0] 
            break # Found a matrix compatible with shape. Use it!

    if matrix is None:
        matrix = np.zeros(shape[1:])

    const = tf.constant(matrix)
    return const #return func(dtype, shape, name)


LW_ACTIVE_HOOKS = {
    'tf.placeholder': placeholder_hook_1
}


class LightweightCore(BaseCore):
    #MODE = 'headless'    
    SKIP_LAYERS = ['TrainNormal', 'TrainReinforce']
    
    def __init__(self, codehq, graph_dict, data_container, session_history,
                 module_provider, layer_extras_reader):
        super().__init__(codehq, graph_dict, data_container,
                         session_history, module_provider,
                         layer_extras_reader=layer_extras_reader, tf_eager=True,
                         skip_layers=self.SKIP_LAYERS)


        

