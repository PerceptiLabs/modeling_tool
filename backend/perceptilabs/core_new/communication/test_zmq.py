import time
import pytest
from unittest.mock import MagicMock

from perceptilabs.core_new.communication.zmq import Server, Client


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


@pytest.fixture(autouse=True)
def shutdown_servers_and_clients():
    global CLIENTS, SERVERS
    
    for client in CLIENTS:
        client.stop()
    CLIENTS = []
    
    for server in SERVERS:
        server.stop()
    SERVERS = []

        
def test_pushed_and_subscribed_message_arrives():
    key = b'key'
    fn = MagicMock()

    create_server().start()
    client = create_client({key: fn})
    client.start()
    
    client.push(b'key', b'hello')
    time.sleep(1.0)
    client.process_messages()
    
    assert fn.call_count == 1
    assert fn.call_args_list[0][0][0] is client
    assert fn.call_args_list[0][0][1] == b'key'
    assert fn.call_args_list[0][0][2] == b'hello'    


def test_pushed_and_non_subscribed_message_does_not_arrive():
    create_server().start()
    client = create_client({})
    client.start()
    
    client.push(b'key', b'hello')
    time.sleep(1.0)
    assert client.messages_received == 0
    

def test_two_clients_receive_the_same_messages():
    key = b'key'
    fn1 = MagicMock()
    fn2 = MagicMock()    

    create_server().start()
    
    c1 = create_client({key: fn1})
    c1.start()
    
    c2 = create_client({key: fn2})    
    c2.start()    
    
    c1.push(b'key', b'hello from 1')
    c2.push(b'key', b'hello from 2')    
    time.sleep(1.0)
    c1.process_messages()
    c2.process_messages()
    
    assert fn1.call_count == 2
    assert fn2.call_count == 2

    c1_value1 = fn1.call_args_list[0][0][2]
    c1_value2 = fn1.call_args_list[1][0][2]    

    c2_value1 = fn2.call_args_list[0][0][2]
    c2_value2 = fn2.call_args_list[1][0][2]    
    
    assert c1_value1 == c2_value1
    assert c1_value2 == c2_value2

