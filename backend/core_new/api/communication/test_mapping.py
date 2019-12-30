import pytest
import queue
import time
import zmq

from mapping import MapServer, MapClient

@pytest.fixture(autouse=True)
def server():
    server = MapServer(
        'tcp://*:5556',
        'tcp://*:5557',
        'tcp://*:5558'
    )
    yield server
    server.stop()

    
@pytest.fixture(autouse=True)
def client():
    client = MapClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )    
    yield client
    client.stop()

@pytest.fixture(autouse=True)
def client2():
    client = MapClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )    
    yield client
    client.stop()

    
def test_client_server_queued_message_is_stored(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    
    assert (b'key') in client.messages
    assert client.messages[b'key'].key == b'key'
    assert client.messages[b'key'].body == b'value'

    
def test_client_server_stopped_client_is_empty(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    assert client.messages != {}
    
    client.stop()
    assert client.messages == {}

    
def test_client_server_restarted_client_catches_up(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    assert client.messages != {}    
    
    client.stop()
    assert client.messages == {}
    
    client.start()
    time.sleep(0.3)
    assert client.messages != {}


def test_second_client_receives_message(server, client, client2):
    server.start(); client.start(); client2.start()

    client.put('update-set', b'key_1', b'value_1')
    client2.put('update-set', b'key_2', b'value_2')
    time.sleep(0.3)    

    assert (b'key_1') in client.messages
    assert (b'key_2') in client.messages    
    assert (b'key_1') in client2.messages
    assert (b'key_2') in client2.messages    
    
    
    
