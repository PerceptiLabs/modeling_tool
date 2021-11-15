import os
import logging

logger = logging.getLogger(__name__)


def get_layer_definition(type_: str):
    assert isinstance(type_, str)
    from perceptilabs.layers.definitions import DEFINITION_TABLE_TF2X
    return DEFINITION_TABLE_TF2X.get(type_, None)


def get_layer_builder(type_: str):
    assert isinstance(type_, str)

    meta = get_layer_definition(type_)

    if meta is not None:
        return meta.builder_class()
    else:
        from perceptilabs.layers.specbase import DummySpec, DummyBuilder
        return DummyBuilder()


def try_cast(value, type_, default=None):
    try:
        return type_(value)        
    except:
        return default


def resolve_checkpoint_path(specs):
    """ Method returns the modified checkpoint_path so that it works with the OS being used. 
            Method also checks for the checkpoint in the directory. It creates the directory if it doesn't exist.

        Args:
            dict_ : network dict corresponding to particular layer

        Returns:
            checkpoint_path: modified checkpoint path corresponding to the OS.
    """
    import platform
    ckpt_path = specs['checkpoint']['path']  
    if '//' in ckpt_path:
        if platform.system() == 'Windows':
            ckpt_path = ckpt_path.split('//')[1]
        else:
            new_ckpt_path = os.path.sep+ckpt_path.split(2*os.path.sep)[1] # Sometimes frontend repeats the directory path. /<dir-path>//<dir-path>/model.ckpt-1
            logger.warning(
                f"Splitting malformed checkpoint path: '{ckpt_path}'. "
                f"New path: '{new_ckpt_path}'"
            )
            ckpt_path = new_ckpt_path
    
    ckpt_path = ckpt_path.replace('\\', '/')
    if os.path.basename(os.path.normpath(ckpt_path)) != 'checkpoint':
        logger.error(f"The given path '{ckpt_path}' is not a valid checkpoint path.")
    if not os.path.isdir(ckpt_path):
        os.makedirs(ckpt_path, exist_ok=True)
    return ckpt_path


def resolve_tf1x_activation_name(specs):
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
        logger.warning(f"layer {layer_id} specified activation {activation}, but it was not found in tf1x activations table. No activation will be used for this layer")

    return func_name

def resolve_tf1x_stop_cond(specs):
    table = ["Epochs", "TargetAccuracy"]

    stop_cond = specs['Properties']['Stop_condition']
    if stop_cond not in table:
        raise NotImplementedError(f"Stop condition {stop_cond} is not yet implemented")


    stop_condition = [x for x in table if x == stop_cond][0]
    
    return stop_condition


