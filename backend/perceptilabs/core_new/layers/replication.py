import numpy as np
from collections import namedtuple

from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import *


""" WARNING: MUST BE SORTED BY MOST GENERAL LAYER FIRST """
BASE_TO_REPLICA_MAP = {
    Tf1xClassificationLayer: Tf1xClassificationLayerReplica,    
    DataLayer: DataLayerReplica,
    Tf1xLayer: Tf1xLayerReplica,
}
REPLICA_TO_BASE_MAP = {replica.__name__: base for base, replica in BASE_TO_REPLICA_MAP.items()}


ReplicatedProperty = namedtuple('ReplicatedProperty', ['name', 'type', 'default'])


""" WARNING: MUST BE SORTED BY MOST GENERAL LAYER FIRST """
REPLICATED_PROPERTIES_TABLE = {
    Tf1xClassificationLayer: [
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
        ReplicatedProperty('layer_gradients', dict, lambda _: dict()),
        ReplicatedProperty('layer_weights', dict, lambda _: dict()),
        ReplicatedProperty('layer_biases', dict, lambda _: dict()),
        ReplicatedProperty('layer_outputs', dict, lambda _: dict()),
        ReplicatedProperty('batch_size', int, -1),
        ReplicatedProperty('is_paused', bool, False),
        ReplicatedProperty('training_iteration', int, -1),
        ReplicatedProperty('validation_iteration', int, -1),        
        ReplicatedProperty('testing_iteration', int, -1),
        ReplicatedProperty('progress', (np.float32, float), -1),
    ],
    DataLayer: [
        ReplicatedProperty('sample', ((np.float32, float), np.ndarray), lambda _: np.empty(())),
        ReplicatedProperty('size_training', int, -1),
        ReplicatedProperty('size_validation', int, -1),
        ReplicatedProperty('size_testing', int, -1),
        ReplicatedProperty('variables', dict, lambda _: dict())
    ], 
    Tf1xLayer: [
        ReplicatedProperty('variables', dict, lambda _: dict())
    ]

}

def verify_general_layers_first():
    for x in REPLICATED_TABLES_PROPERTIES:
        pass # TODO: implement this :)
    
    
