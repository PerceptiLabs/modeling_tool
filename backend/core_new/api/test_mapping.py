import pytest
import pickle
import queue
import time
import zmq
from unittest.mock import MagicMock

from core_new.api.mapping import MapServer, MapClient, ByteMap, ByteSequence


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

    
@pytest.fixture(autouse=True)    
def map2_2():
    map2 = ByteMap(
        'map2',
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )
    yield map2
    map2.stop()

@pytest.fixture(autouse=True)    
def seq1():
    seq1 = ByteSequence(
        'seq1',
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        'tcp://localhost:5558'
    )
    yield seq1
    seq1.stop()

    
def wait_for_condition(fn, timeout=5.0):
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < timeout:
        if fn(0):
            return True        
        time.sleep(0.01)
    return False    
    

def test_client_server_queued_message_is_stored(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    
    assert wait_for_condition(lambda _: (b'key') in client.mapping)
    assert wait_for_condition(lambda _: client.mapping[b'key'] == b'value')

    
def test_client_server_delete_works(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    assert wait_for_condition(lambda _: (b'key') in client.mapping)
    
    client.put('update-del', b'key')
    assert wait_for_condition(lambda _: (b'key') not in client.mapping)

    
def test_client_server_delete_works_with_subtree(server, client3):
    server.start(); client3.start()
    
    client3.put('update-set', b'key', b'value')
    assert wait_for_condition(lambda _: (b'key') in client3.mapping)
    
    client3.put('update-del', b'key')
    assert wait_for_condition(lambda _: (b'key') not in client3.mapping)


def test_client_message_set_callback_is_called(server, client):
    server.start()
    client.start()

    callback = MagicMock()
    client.set_callbacks(on_set=callback)
    client.put('update-set', b'key', b'value')
    
    assert wait_for_condition(lambda _: callback.called)


def test_client_message_delete_callback_is_called(server, client):
    server.start()
    client.start()

    callback = MagicMock()
    client.set_callbacks(on_delete=callback)
    client.put('update-set', b'key', b'value')
    client.put('update-del', b'key')
    
    assert wait_for_condition(lambda _: callback.called)
    
    
def test_client_server_stopped_client_is_empty(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    assert wait_for_condition(lambda _: client.mapping != {})
    
    client.stop()
    assert wait_for_condition(lambda x: client.mapping == {})    

    
def test_client_server_can_delete_message(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    assert wait_for_condition(lambda _: client.mapping != {})
    
    client.put('update-del', b'key')
    assert wait_for_condition(lambda _: client.mapping == {})

    
def test_client_server_restarted_client_catches_up(server, client):
    server.start(); client.start()
    
    client.put('update-set', b'key', b'value')
    assert wait_for_condition(lambda _: client.mapping != {})
    
    client.stop()
    assert wait_for_condition(lambda _: client.mapping == {})
    
    client.start()
    assert wait_for_condition(lambda _: client.mapping != {})


def test_second_client_receives_message(server, client, client2):
    server.start(); client.start(); client2.start()

    client.put('update-set', b'key_1', b'value_1')
    client2.put('update-set', b'key_2', b'value_2')

    assert wait_for_condition(lambda _: (b'key_1') in client.mapping)
    assert wait_for_condition(lambda _: (b'key_2') in client.mapping)
    assert wait_for_condition(lambda _: (b'key_1') in client2.mapping)
    assert wait_for_condition(lambda _: (b'key_2') in client2.mapping)

    
def test_clients_with_different_subtree_are_disjoint(server, client3, client4):
    server.start(); client3.start(); client4.start()

    client3.put('update-set', b'key_1', b'value_1')
    client4.put('update-set', b'key_2', b'value_2')
    
    assert wait_for_condition(lambda _: (b'key_1') in client3.mapping)
    assert wait_for_condition(lambda _: (b'key_2') in client4.mapping)
    
    assert wait_for_condition(lambda _: (b'key_2') not in client3.mapping)
    assert wait_for_condition(lambda _: (b'key_1') not in client4.mapping)


def test_client_all_values_are_present_in_sequence(server, client):
    server.start(); client.start()
    n_values = 1000

    f = lambda n: ((str(i).encode(), str(i+1).encode()) for i in range(n))

    for key, value in f(n_values):
        client.put('update-set', key, value)

    def all_values_present():
        seq = client.sequence
        for item in f(n_values):
            if item not in seq:
                return False
        return True

    assert wait_for_condition(lambda _: all_values_present())


def test_client_all_values_are_present_in_sequence_multi_client(server, client, client2):
    server.start(); client.start(); client2.start()
    n_values = 1000

    f = lambda n: ((str(i).encode(), str(i+1).encode()) for i in range(n))

    for counter, (key, value) in enumerate(f(n_values)):
        if counter % 2 == 0:
            client.put('update-set', key, value)
        else:
            client2.put('update-set', key, value)

    def all_values_present():
        seq = client.sequence
        for item in f(n_values):
            if item not in seq:
                return False
        return True

    assert wait_for_condition(lambda _: all_values_present())


def test_multi_client_sequences_are_identical(server, client, client2):
    server.start(); client.start(); client2.start()
    n_values = 1000

    f = lambda n: ((str(i).encode(), str(i+1).encode()) for i in range(n))

    for counter, (key, value) in enumerate(f(n_values)):
        if counter % 2 == 0:
            client.put('update-set', key, value)
        else:
            client2.put('update-set', key, value)

    def all_values_present_with_same_order():
        if len(client.sequence) != n_values or len(client2.sequence) != n_values:
            return False
        
        seq1 = client.sequence
        seq2 = client2.sequence
        for a, b in zip(seq1, seq2):
            if a != b:
                return False
        return True

    assert wait_for_condition(lambda _: all_values_present_with_same_order())

    
def test_byte_maps_with_different_names_are_disjoint(server, map1, map2):
    server.start(); map1.start(); map2.start()
    
    map1[b'key_1'] = b'value_1'
    map2[b'key_2'] = b'value_2'

    assert wait_for_condition(lambda _: (b'key_1') in map1)
    assert wait_for_condition(lambda _: (b'key_2') in map2)
    assert wait_for_condition(lambda _: (b'key_2') not in map1)
    assert wait_for_condition(lambda _: (b'key_1') not in map2)

    
def test_byte_maps_with_same_names_are_equal(server, map2, map2_2):
    server.start(); map2.start(); map2_2.start()
    
    map2[b'key_1'] = b'value_1'
    map2_2[b'key_2'] = b'value_2'

    assert wait_for_condition(lambda _: (b'key_1') in map2)
    assert wait_for_condition(lambda _: (b'key_2') in map2)
    assert wait_for_condition(lambda _: (b'key_1') in map2_2)
    assert wait_for_condition(lambda _: (b'key_2') in map2_2)

    
def test_byte_sequence_appended_value_is_present(server, seq1):
    server.start(); seq1.start()
    seq1.append(b'hello')
    assert wait_for_condition(lambda _: list(seq1) == [b'hello'])

    
def test_byte_sequence_appended_value_is_not_present(server, seq1):
    server.start(); seq1.start()
    seq1.append(b'hello')
    assert wait_for_condition(lambda _: list(seq1) == [b'hello'])    
    del seq1[0]
    assert wait_for_condition(lambda _: list(seq1) == [])

    
def test_byte_sequence_appended_values_are_present(server, seq1):
    server.start(); seq1.start()
    seq1.append(b'abc')
    seq1.append(b'xyz')    
    assert wait_for_condition(lambda _: set(seq1) == set([b'abc', b'xyz']))

    
def test_byte_sequence_delete_moves_second_item_up(server, seq1):
    server.start(); seq1.start()
    seq1.append(b'abc')
    seq1.append(b'xyz')
    
    assert wait_for_condition(lambda _: set(seq1) == set([b'abc', b'xyz']))
    list1 = list(seq1)

    del seq1[0]
    del list1[0]
    assert wait_for_condition(lambda _: list(seq1) == list1)    



    

    
