from collections import namedtuple
from typing import Dict
import logging


from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.utils import *
from perceptilabs.core_new.graph.utils import sanitize_layer_name


log = logging.getLogger(__name__)


TEMPLATES_DIRECTORY = 'core_new/layers/templates/' # Relative to the package root directory


class LayerDef:
    """Defines a layer class."""
    def __init__(self, base_class, template_file, template_macro, macro_parameters):
        """Specifies the nature of a layer. Each layer extends a base class and the implementation comes packaged in a jinja2 template macro that can be rendered into python code. 
        The implementation rendered will vary according to the specifications made in the frontend.

        Each macro takes a set of parameters as input. In most cases, these will be resolved from the Json network/graph produced by the frontend. For such cases, the macro parameter will usually be specified by a callable. The callable receives the portion of the Json network related to the layer in question and is expected to return a parsed value. The macro parameter can also be a hard coded value.         
        Args:
            base_class: the base class that this layer implements. 
            template_file: the jinja2 template file containing the actual implementation. Must be located in the TEMPLATES_DIRECTORY
            template_macro: the name of a jinja2 macro, available in the template file, that renders the implementation.
            macro_parameters: a dictionary of keys mapping to a value (or callable returning a value). This key-value pair will be passed as an argument to the jinja2 macro during rendering. 
        """
        self.base_class = base_class
        self.template_file = template_file
        self.template_macro = template_macro
        self.macro_parameters = macro_parameters

def resolve_checkpoint_path(specs):
    import os
    if len(specs['checkpoint']) >= 3:
        return os.path.join(specs['checkpoint'][2], '1')
    else:
        return None
        
        
DEFINITION_TABLE = {
    'DataData': LayerDef(
        DataLayer,
        'datadata.j2',
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
    'ProcessGrayscale' : LayerDef(
        Tf1xLayer,
        'tf1x.j2',
        'layer_tf1x_grayscale',
        {}
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
            'activation': resolve_tf1x_activation_name,
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
            'activation': resolve_tf1x_activation_name,            
            'pool': lambda specs: specs['Properties']['PoolBool'],
            'pooling': lambda specs: specs['Properties']['Pooling'],
            'pool_area': lambda specs: specs['Properties']['Pool_area'],
            'pool_stride': lambda specs: specs['Properties']['Pool_stride'],            
        }
    ),
    'TrainNormal': LayerDef(
        ClassificationLayer,
        'tf1x_classification.j2',
        'layer_tf1x_classification',
        {
            'output_layer': lambda specs: [sanitize_layer_name(x) for true_id, x in specs['backward_connections'] if true_id != specs['Properties']['Labels']][0],
            'target_layer': lambda specs: [sanitize_layer_name(x) for true_id, x in specs['backward_connections'] if true_id == specs['Properties']['Labels']][0],
            'n_epochs': lambda specs: specs['Properties']['Epochs'],
            'loss_function': lambda specs: specs['Properties']['Loss'],
            'class_weights': lambda specs: specs['Properties']['Class_weights'],
            'optimizer': resolve_tf1x_optimizer,
            'learning_rate': lambda specs: specs['Properties']['Learning_rate'],
            'decay_steps': lambda specs: specs['Properties']['Decay_steps'],
            'decay_rate': lambda specs: specs['Properties']['Decay_rate'],
            'momentum': lambda specs: specs['Properties']['Momentum'],
            'beta1': lambda specs: specs['Properties']['Beta_1'],
            'beta2': lambda specs: specs['Properties']['Beta_2'],
            'distributed': lambda specs: specs['Properties']['Distributed'],
            'export_directory': resolve_checkpoint_path
        }
    )
}
