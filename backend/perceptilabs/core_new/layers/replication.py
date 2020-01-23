from collections import namedtuple

from core_new.layers import *
from core_new.layers.replicas import *


ReplicaDef = namedtuple(
    'ReplicaDef',
    [
        'replicated_class',
        'replica_class',
        'properties',
    ]
)
     
    
DEFINITION_TABLE = [
    ReplicaDef(
        DataLayer,
        DataLayerReplica,
        [
            'sample',
            'size_training',
            'size_validation',
            'variables',
        ]
]
