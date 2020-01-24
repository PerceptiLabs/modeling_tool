from collections import namedtuple
from typing import Dict
import logging


from perceptilabs.core_new.layers import *


log = logging.getLogger(__name__)


LayerDef = namedtuple(
    'LayerDef',
    [
        'base_class',
        'template_file',        
        'template_macro',
        'macro_parameters',
    ]
)


def get_tf1x_activation(specs):
    table = {
        None: None,
        '': None,
        'Sigmoid': 'tf.compat.v1.sigmoid',
        'ReLU': 'tf.compat.v1.nn.relu',
        'Tanh': 'tf.compat.v1.tanh'
    }

    activation = specs['Properties']['Activation_function']
    func_name = table.get(activation)
    if activation not in table:
        layer_id = '<not implemented>'
        log.warning(f"layer {layer_id} specified activation {activation}, but it was not found in tf1x activations table. No activation will be used for this layer")

    return func_name


DEFINITION_TABLE = {
    'DataData': LayerDef(
        DataLayer,
        'datadata2.j2',
        'layer_datadata',
        {
            'sources': lambda specs: specs['Properties']['accessProperties']['Sources'],
            'partitions': lambda specs: specs['Properties']['accessProperties']['Partition_list'],
            'batch_size': lambda specs: specs['Properties']['accessProperties']['Batch_size'],
            'shuffle': lambda specs: specs['Properties']['accessProperties']['Shuffle_data'],
            'selected_columns': lambda specs: specs['Properties']['accessProperties']['Columns'],
            'seed': 0,
            'lazy': False,
            'shuffle_buffer_size': None,
        }
    ),
    'ProcessReshape': LayerDef(
        Tf1xLayer,
        'tf1x.j2',
        'layer_tf1x_reshape',        
        {
            'shape': lambda specs: specs['Properties']['Shape'],
            'permutation': lambda specs: specs['Properties']['Permutation']
        }
    ),
    'ProcessOneHot': LayerDef(
        Tf1xLayer,
        'tf1x.j2',
        'layer_tf1x_one_hot',
        {
            'n_classes': lambda specs: specs['Properties']['N_class']
        }
    ),
    'DeepLearningFC':  LayerDef(
        Tf1xLayer,
        'tf1x.j2',
        'layer_tf1x_fully_connected',
        {
            'n_neurons': lambda specs: specs['Properties']['Neurons'],
            'activation': get_tf1x_activation,
            'dropout': lambda specs: specs['Properties']['Dropout'],
            'keep_prob': lambda specs: specs['Properties']['Keep_prob']
        }
    ),
    'DeepLearningConv':  LayerDef(
        Tf1xLayer,
        'tf1x.j2',
        'layer_tf1x_conv',
        {
            'conv_dim': lambda specs: specs['Properties']['Conv_dim'],
            'patch_size': lambda specs: specs['Properties']['Patch_size'],
            'feature_maps': lambda specs: specs['Properties']['Feature_maps'],
            'stride': lambda specs: specs['Properties']['Stride'],
            'padding': lambda specs: specs['Properties']['Padding'][1:-1],
            'dropout': lambda specs: specs['Properties']['Dropout'],
            'keep_prob': lambda specs: specs['Properties']['Keep_prob'],
            'activation': get_tf1x_activation,            
            'pool': lambda specs: specs['Properties']['PoolBool'],
            'pooling': lambda specs: specs['Properties']['Pooling'],
            'pool_area': lambda specs: specs['Properties']['Pool_area'],
            'pool_stride': lambda specs: specs['Properties']['Pool_stride'],            
        }
    ),
    'TrainNormal': LayerDef(
        Tf1xClassificationLayer,
        'tf1x_classification.j2',
        'layer_tf1x_classification',
        {
            'output_layer': lambda specs: [x for x in specs['backward_connections'] if x != specs['Properties']['Labels']][0],
            'target_layer': lambda specs: specs['Properties']['Labels'],
            'n_epochs': lambda specs: specs['Properties']['Epochs'],
            'loss_function': lambda specs: specs['Properties']['Loss'],
            'class_weights': lambda specs: specs['Properties']['Class_weights'],
            'optimizer': lambda specs: specs['Properties']['Optimizer'],
            'learning_rate': lambda specs: specs['Properties']['Learning_rate'],
            'decay_steps': lambda specs: specs['Properties']['Decay_steps'],
            'decay_rate': lambda specs: specs['Properties']['Decay_rate'],
            'momentum': lambda specs: specs['Properties']['Momentum'],
            'beta1': lambda specs: specs['Properties']['Beta_1'],
            'beta2': lambda specs: specs['Properties']['Beta_2'],
            'distributed': lambda specs: specs['Properties']['Distributed']
        }
    )
}
