import time
import pytest
from unittest.mock import MagicMock

from perceptilabs.core_new.communication.zmq import Server, Client
from perceptilabs.utils import wait_for_condition

SERVERS = []
CLIENTS = []


def create_server():
    server = Server(
        'tcp://*:5556',
        'tcp://*:5557',
    )
    SERVERS.append(server)    
    return server


def create_client(handlers):
    client = Client(
         'tcp://localhost:5556',
         'tcp://localhost:5557',
        handlers
    )
    CLIENTS.append(client)
    return client


def shutdown_servers_and_clients_fn():
    global CLIENTS, SERVERS
    
    for client in CLIENTS:
        client.stop()
    CLIENTS = []
    
    for server in SERVERS:
        server.stop()
    SERVERS = []

    
@pytest.fixture(autouse=True)
def shutdown_servers_and_clients():
    shutdown_servers_and_clients_fn()

    
def test_pushed_and_subscribed_message_arrives():
    key = b'key'
    fn = MagicMock()

    server = create_server()
    server.start()
    client = create_client({key: fn})
    client.start()

    wait_for_condition(lambda _: server.is_running)
    wait_for_condition(lambda _: client.is_running)    
    
    client.push(b'key', b'hello')

    def cond(_):
        client.process_messages()
        return fn.call_count == 1
    
    assert wait_for_condition(cond)
    assert fn.call_args_list[0][0][0] is client
    assert fn.call_args_list[0][0][1] == b'key'
    assert fn.call_args_list[0][0][2] == b'hello'    

    
def test_pushed_and_subscribed_message_arrives_repeated():
    for i in range(100):
        print('Attempt', i)
        key = b'key'
        fn = MagicMock()
        
        server = create_server()
        server.start()
        client = create_client({key: fn})
        client.start()
        
        wait_for_condition(lambda _: server.is_running)
        wait_for_condition(lambda _: client.is_running)    
        
        client.push(b'key', b'hello')
        
        def cond(_):
            client.process_messages()
            return fn.call_count == 1
    
        assert wait_for_condition(cond)
        assert fn.call_args_list[0][0][0] is client
        assert fn.call_args_list[0][0][1] == b'key'
        assert fn.call_args_list[0][0][2] == b'hello'

        shutdown_servers_and_clients_fn()


def test_pushed_and_non_subscribed_message_does_not_arrive():
    server = create_server()
    server.start()
    client = create_client({})
    client.start()

    wait_for_condition(lambda _: server.is_running)
    wait_for_condition(lambda _: client.is_running)    
    
    
    client.push(b'key', b'hello')
    time.sleep(15)
    client.process_messages()
    assert client.messages_received == 0
    

def test_two_clients_receive_the_same_messages():
    key = b'key'
    fn1 = MagicMock()
    fn2 = MagicMock()    

    server = create_server()
    server.start()
    c1 = create_client({b'key': fn1})
    c1.start()
    c2 = create_client({b'key': fn2})    
    c2.start()    

    wait_for_condition(lambda _: server.is_running)
    wait_for_condition(lambda _: c1.is_running)
    wait_for_condition(lambda _: c2.is_running)        
    
    c1.push(b'key', b'hello from 1')
    c2.push(b'key', b'hello from 2')    

    def cond1(_):
        c1.process_messages()
        return fn1.call_count == 2
    def cond2(_):
        c2.process_messages()
        return fn2.call_count == 2
    
    assert wait_for_condition(cond1)
    assert wait_for_condition(cond2)

    c1_value1 = fn1.call_args_list[0][0][2]
    c1_value2 = fn1.call_args_list[1][0][2]    

    c2_value1 = fn2.call_args_list[0][0][2]
    c2_value2 = fn2.call_args_list[1][0][2]    
    
    assert c1_value1 == c2_value1
    assert c1_value2 == c2_value2


def test_two_clients_receive_the_same_messages_repeated():
    for i in range(100):
        print('Attempt', i)
        key = b'key'
        fn1 = MagicMock()
        fn2 = MagicMock()    
        
        server = create_server()
        server.start()
        c1 = create_client({b'key': fn1})
        c1.start()
        c2 = create_client({b'key': fn2})    
        c2.start()    
        
        wait_for_condition(lambda _: server.is_running)
        wait_for_condition(lambda _: c1.is_running)
        wait_for_condition(lambda _: c2.is_running)        
        
        c1.push(b'key', b'hello from 1')
        c2.push(b'key', b'hello from 2')    
        

        def cond1(_):
            c1.process_messages()
            return fn1.call_count == 2
        def cond2(_):
            c2.process_messages()
            return fn2.call_count == 2
    
        assert wait_for_condition(cond1)
        assert wait_for_condition(cond2)

        c1_value1 = fn1.call_args_list[0][0][2]
        c1_value2 = fn1.call_args_list[1][0][2]    
        
        c2_value1 = fn2.call_args_list[0][0][2]
        c2_value2 = fn2.call_args_list[1][0][2]    

        assert c1_value1 == c2_value1
        assert c1_value2 == c2_value2

        shutdown_servers_and_clients_fn()

    
