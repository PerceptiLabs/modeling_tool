import pytest
import queue
import time
import zmq


from mapping import MapServer, MapClient, ByteMap


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

    
@pytest.fixture(autouse=True)
def client3():
    client = MapClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558',
        'subtree1'
    )    
    yield client
    client.stop()

    
@pytest.fixture(autouse=True)
def client4():
    client = MapClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558',
        'subtree2'
    )    
    yield client
    client.stop()

    
@pytest.fixture(autouse=True)    
def map1():
    map1 = ByteMap(
        'map1',
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )
    yield map1
    map1.stop()

    
@pytest.fixture(autouse=True)    
def map2():
    map2 = ByteMap(
        'map2',
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )
    yield map2
    map2.stop()

    
def test_client_server_queued_message_is_stored(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    
    assert (b'key') in client.mapping
    assert client.mapping[b'key'] == b'value'

    
def test_client_server_stopped_client_is_empty(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    assert client.mapping != {}
    
    client.stop()
    assert client.mapping == {}

    
def test_client_server_can_delete_message(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    assert client.mapping != {}
    
    client.put('update-del', b'key')
    time.sleep(0.3)
    assert client.mapping == {}

    
def test_client_server_restarted_client_catches_up(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    time.sleep(0.3)
    assert client.mapping != {}    
    
    client.stop()
    assert client.mapping == {}
    
    client.start()
    time.sleep(0.3)
    assert client.mapping != {}


def test_second_client_receives_message(server, client, client2):
    server.start(); client.start(); client2.start()

    client.put('update-set', b'key_1', b'value_1')
    client2.put('update-set', b'key_2', b'value_2')
    time.sleep(0.3)    

    assert (b'key_1') in client.mapping
    assert (b'key_2') in client.mapping    
    assert (b'key_1') in client2.mapping
    assert (b'key_2') in client2.mapping

    
def test_clients_with_different_subtree_are_disjoint(server, client3, client4):
    server.start(); client3.start(); client4.start()

    client3.put('update-set', b'key_1', b'value_1')
    client4.put('update-set', b'key_2', b'value_2')
    time.sleep(0.3)    
    
    assert (b'key_1') in client3.mapping
    assert (b'key_2') in client4.mapping
    
    assert (b'key_2') not in client3.mapping    
    assert (b'key_1') not in client4.mapping    


def test_byte_maps_are_disjoint(server, map1, map2):
    server.start(); map1.start(); map2.start()
    
    map1[b'key_1'] = b'value_1'
    map2[b'key_2'] = b'value_2'
    time.sleep(0.3)

    assert (b'key_1') in map1
    assert (b'key_2') in map2
    assert (b'key_2') not in map1
    assert (b'key_1') not in map2

