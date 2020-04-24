"""The purpose of replication:

    *The deployed core contains all the values and parameters associated with the current training session.
    *A subset of these values will be visualized by the frontend.
    *That subset will be sent from the deployed core to the main core in the form of replica classes.

Each replica is an immutable and serializable snapshot of a layer class running on the deployed core. These are serialized together with a graph code, enabling the main core to work with snapshots of the evolving trainin graph over the course of the training.
"""


import numpy as np
from collections import namedtuple

from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import *


"""BASE_TO_REPLICA_MAP Specifies a replication pair. Both will implement a common base class. 

WARNING: MUST HAVE SUBCLASSES APPEARING FIRST (if not, e.g., a training layer could be erroneously replicated as a data layer, which would hide a lot of information to the core)."""
BASE_TO_REPLICA_MAP = {
    ClassificationLayer: ClassificationLayerReplica,  
    ObjectDetectionLayer: ObjectDetectionLayerReplica,  
    DataLayer: DataLayerReplica,
    Tf1xLayer: Tf1xLayerReplica,
    InnerLayer: InnerLayerReplica,        
}
REPLICA_TO_BASE_MAP = {replica.__name__: base for base, replica in BASE_TO_REPLICA_MAP.items()}


class ReplicatedProperty:
    """Specifies how a property is replicated."""
    def __init__(self, name, type, default):
        """        
        Args:
            name: a string matching the property name of a base class and a constructor argument of a replica class.
            type: an object or a tuple of objects. In the case of a tuple, either will be considered a valid return value during replication.
            default: a primitive value or a callable. Callables are called with a 'None' argument and are expected to return a default value (useful for by-reference default values).
        """
        self.name = name
        self.type = type
        self.default = default
        

"""REPLICATED_PROPERTIES_TABLE specifies which properties of a base class is replicated. 

WARNING: MUST HAVE SUBCLASSES APPEARING FIRST"""
REPLICATED_PROPERTIES_TABLE = {
    ClassificationLayer: [
        ReplicatedProperty('sample', (np.float32, np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('size_training', int, -1),
        ReplicatedProperty('size_validation', int, -1),
        ReplicatedProperty('size_testing', int, -1),
        ReplicatedProperty('epoch', int, -1),        
        ReplicatedProperty('variables', dict, lambda _: dict()),
        ReplicatedProperty('accuracy_training', (np.float32, float), -1),
        ReplicatedProperty('accuracy_validation', (np.float32, float), -1),
        ReplicatedProperty('accuracy_testing', (np.float32, float), -1),
        ReplicatedProperty('loss_training', (np.float32, float), -1),
        ReplicatedProperty('loss_validation', (np.float32, float), -1),        
        ReplicatedProperty('loss_testing', (np.float32, float), -1),
        ReplicatedProperty('status', str, '<none>'),
        ReplicatedProperty('layer_gradients', dict, {}),
        ReplicatedProperty('layer_weights', dict, lambda _: dict()),
        ReplicatedProperty('layer_biases', dict, lambda _: dict()),
        ReplicatedProperty('layer_outputs', dict, lambda _: dict()),
        ReplicatedProperty('batch_size', int, -1),
        ReplicatedProperty('training_iteration', int, -1),
        ReplicatedProperty('validation_iteration', int, -1),        
        ReplicatedProperty('testing_iteration', int, -1),
        ReplicatedProperty('progress', (np.float32, float), -1),
        ReplicatedProperty('export_modes', list, []),        
    ],
    ObjectDetectionLayer: [
        ReplicatedProperty('sample', (np.float32, np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('size_training', int, -1),
        ReplicatedProperty('size_validation', int, -1),
        ReplicatedProperty('size_testing', int, -1),
        ReplicatedProperty('epoch', int, -1),        
        ReplicatedProperty('variables', dict, lambda _: dict()),
        ReplicatedProperty('accuracy_training', (np.float32, float), -1),
        ReplicatedProperty('accuracy_validation', (np.float32, float), -1),
        ReplicatedProperty('accuracy_testing', (np.float32, float), -1),
        ReplicatedProperty('image_accuracy', (np.float32, float), -1),
        ReplicatedProperty('loss_training', (np.float32, float), -1),
        ReplicatedProperty('loss_validation', (np.float32, float), -1),        
        ReplicatedProperty('loss_testing', (np.float32, float), -1),
        ReplicatedProperty('loss_classification_training', (np.float32, float), -1),
        ReplicatedProperty('loss_classification_validation', (np.float32, float), -1),        
        ReplicatedProperty('loss_classification_testing', (np.float32, float), -1),
        ReplicatedProperty('loss_bbox_training', (np.float32, float), -1),
        ReplicatedProperty('loss_bbox_validation', (np.float32, float), -1),        
        ReplicatedProperty('loss_bbox_testing', (np.float32, float), -1),
        ReplicatedProperty('get_predicted_objects', (np.float32, np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('get_predicted_classes', (np.float32, np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('get_predicted_normalized_boxes', (np.float32, np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('grid_size',int, 7),
        ReplicatedProperty('num_class', int, 3),
        ReplicatedProperty('num_box', int, 2),
        ReplicatedProperty('classes', list, []),
        ReplicatedProperty('lambdacoord', (np.float32, float), 5),
        ReplicatedProperty('lambdanoobj', (np.float32, float), 0.5),
        ReplicatedProperty('get_input_data_node', str,''),
        ReplicatedProperty('status', str, '<none>'),
        ReplicatedProperty('layer_gradients', dict, lambda _: dict()),
        ReplicatedProperty('layer_weights', dict, lambda _: dict()),
        ReplicatedProperty('layer_biases', dict, lambda _: dict()),
        ReplicatedProperty('layer_outputs', dict, lambda _: dict()),
        ReplicatedProperty('batch_size', int, -1),
        ReplicatedProperty('training_iteration', int, -1),
        ReplicatedProperty('validation_iteration', int, -1),        
        ReplicatedProperty('testing_iteration', int, -1),
        ReplicatedProperty('progress', (np.float32, float), -1),
        ReplicatedProperty('export_modes', list, []),        
    ],
    DataLayer: [
        ReplicatedProperty('sample', ((np.float32, float), np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('size_training', int, -1),
        ReplicatedProperty('size_validation', int, -1),
        ReplicatedProperty('size_testing', int, -1),
        ReplicatedProperty('variables', dict, lambda _: dict())
    ],
    Tf1xLayer: [
        ReplicatedProperty('variables', dict, lambda _: dict()),
    ],
    InnerLayer: [
        ReplicatedProperty('variables', dict, lambda _: dict()),
    ],
}


def _assert_subclasses_come_first(class_list, list_name):
    for idx, c1 in enumerate(class_list[:-1]):
        for c2 in class_list[idx+1:]:
            if issubclass(c2, c1):
                message = f"Class {c2.__name__} is a subclass of {c1.__name__} and appears later in {list_name}. Re-arrange the order to make sure the more general classes appear first."
                raise ValueError(message)

_assert_subclasses_come_first(list(BASE_TO_REPLICA_MAP.keys()), 'BASE_TO_REPLICA_CLASS')
_assert_subclasses_come_first(list(REPLICATED_PROPERTIES_TABLE.keys()), 'REPLICATED_PROPERTIES_TABLE')


def _assert_base_classes_have_all_properties(base_to_replica_map, replicated_properties_table):
    for base_class in base_to_replica_map.keys():
        replicated_properties = replicated_properties_table.get(base_class, [])

        for repl_prop in replicated_properties:
            if not hasattr(base_class, repl_prop.name) or not isinstance(getattr(base_class, repl_prop.name), property):
                raise ValueError(f"Base class {base_class.__name__} has no property named '{repl_prop.name}'")

_assert_base_classes_have_all_properties(BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE)


def _assert_replica_classes_have_all_arguments(base_to_replica_map, replicated_properties_table):
    import inspect
    
    for base_class, replica_class in base_to_replica_map.items():
        replicated_properties = replicated_properties_table.get(base_class, [])
        existing_args = inspect.getargspec(replica_class.__init__).args
        for repl_prop in replicated_properties:
            if repl_prop.name not in existing_args:
                raise ValueError(f"Replica class {replica_class.__name__} constructor has no positional argument named '{repl_prop.name}'")
            
_assert_replica_classes_have_all_arguments(BASE_TO_REPLICA_MAP, REPLICATED_PROPERTIES_TABLE)
