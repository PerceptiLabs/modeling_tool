import time
import pytest
import numpy as np
from unittest.mock import create_autospec, PropertyMock


from core_new.layers import DataLayer, TrainingLayer
from core_new.layers.replicas import DataLayerReplica#, TrainingLayerReplica
from core_new.layers.replicators import DataLayerReplicator, Tf1xClassificationLayerReplicator
from core_new.layers.communication import ZmqServer, ZmqClient


@pytest.mark.integtest
def test_data_layer_properties_are_replicated():
    SESSION_ID = 'sess1'
    LAYER_ID = 'layer1'
    
    server = ZmqServer([])
    client = ZmqClient()
    server.start()
    client.start()
    
    sample = np.random.random((10, 10))
    size_training = 123
    size_validation = 456
    size_testing = 789
    
    layer = create_autospec(DataLayer)
    type(layer).sample = PropertyMock(return_value=sample)
    type(layer).size_training = PropertyMock(return_value=size_training)
    type(layer).size_validation = PropertyMock(return_value=size_validation)
    type(layer).size_testing = PropertyMock(return_value=size_testing)            
     
    replicator = DataLayerReplicator(layer, SESSION_ID, LAYER_ID, server)    
    replica = DataLayerReplica(SESSION_ID, LAYER_ID, client)
    replicator.synchronize()
    
    time.sleep(0.3)
    assert np.all(replica.sample == sample)
    assert np.all(replica.size_training == size_training)
    assert np.all(replica.size_validation == size_validation)
    assert np.all(replica.size_testing == size_testing)            
    client.stop()
    server.stop()

    
@pytest.mark.integtest
def test_training_layer_events_are_replicated():
    SESSION_ID = 'sess1'
    LAYER_ID = 'layer1'
    
    layer = create_autospec(TrainingLayer)

    server = ZmqServer({
        f'{SESSION_ID}+{LAYER_ID}-on_pause': layer.on_pause
    })
    
    client = ZmqClient()
    server.start()
    client.start()
    
    replicator = Tf1xClassificationLayerReplicator(layer, SESSION_ID, LAYER_ID, server)    
    replica = Tf1xClassificationLayerReplica(SESSION_ID, LAYER_ID, client)

    assert layer.on_pause.call_count == 0    
    replica.on_pause()
    
    time.sleep(0.3)
    assert layer.on_pause.call_count == 1
    
    client.stop()
    server.stop()




