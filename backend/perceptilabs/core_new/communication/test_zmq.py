import pytest
import socket
import time

from perceptilabs.utils import loop_until_true
from perceptilabs.core_new.utils import find_free_port
from perceptilabs.core_new.communication.zmq import ZmqClient, ZmqServer, ConnectionTimeout, ConnectionLost, NotConnectedError, ConnectionClosed


@pytest.fixture(scope='function')
def ports():
    port1, port2 = find_free_port(count=2)        
    return port1, port2


@pytest.fixture(scope='function')
def server(ports):
    server = ZmqServer(
        'tcp://*:{}'.format(ports[0]),
        'tcp://*:{}'.format(ports[1]),
    )
    yield server
    server.stop()


@pytest.fixture(scope='function')
def client1(ports):
    client = ZmqClient(
         'tcp://localhost:{}'.format(ports[0]),
         'tcp://localhost:{}'.format(ports[1]),
        tag='client 1'
    )
    return client


@pytest.fixture(scope='function')
def client2(ports):
    client = ZmqClient(
         'tcp://localhost:{}'.format(ports[0]),
         'tcp://localhost:{}'.format(ports[1]),
        tag='client 2'
    )
    yield client
    client.stop()

    
def test_addresses_not_in_use_after_server_stop():

    def do_test():
        server = ZmqServer(
            'tcp://*:5556',
            'tcp://*:5557',
        )
        server.start()
        server.stop()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", 5556))
            s.close()
        except:
            success1 = False
        else:
            success1 = True
            
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", 5557))
            s.close()        
        except:
            success2 = False
        else:
            success2 = True

        return success1 and success2

    for _ in range(5):
        do_test()


def test_addresses_not_in_use_after_server_stop_with_client_connected():

    def do_test():
        server = ZmqServer(
            'tcp://*:5556',
            'tcp://*:5557',
        )

        client = ZmqClient(
            'tcp://localhost:5556',
            'tcp://localhost:5557',
            tag='client'
        )
        
        server.start()
        client.connect()
        server.stop()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", 5556))
            s.close()
        except:
            success1 = False
        else:
            success1 = True
            
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("localhost", 5557))
            s.close()        
        except:
            success2 = False
        else:
            success2 = True

        return success1 and success2

    for _ in range(5):
        do_test()

        
def test_client_raises_timeout_when_no_server(client1):
    with pytest.raises(ConnectionTimeout):
        client1.connect(timeout=2)

        
def test_can_connect_to_server(server, client1):
    server.start()
    try:
        client1.connect()
    except:
        success = False
    else:
        success = True
    assert success

    
def test_sent_message_arrives(server, client1):
    server.start()
    client1.connect()
    client1.send_message(b'hello')

    received_messages = []
    def cond(_):
        received_messages.extend(client1.get_messages())
        return received_messages == [b'hello']
    assert loop_until_true(cond)    


def test_sent_sequence_message_arrives_in_order(server, client1):
    server.start()
    client1.connect()

    sequence = [str(x).encode() for x in range(15)]
    for msg in sequence:
        client1.send_message(msg)

    received_messages = []
    def cond(_):
        received_messages.extend(client1.get_messages())
        return received_messages == sequence
    assert loop_until_true(cond)

    
def test_sent_messages_arrive_from_two_clients(server, client1, client2):
    server.start()
    client1.connect()
    client2.connect()    

    sent_messages = set()
    for i in range(20):
        msg = str(i).encode()        
        if i % 2 == 0:
            client1.send_message(msg)
        else:
            client2.send_message(msg)
        sent_messages.add(msg)

    received_messages1 = set()
    received_messages2 = set()    
    def cond(_):
        received_messages1.update(client1.get_messages())
        received_messages2.update(client2.get_messages())
        return received_messages1 == received_messages2 == sent_messages
    assert loop_until_true(cond)


def test_sent_messages_arrive_in_same_order_for_both_clients(server, client1, client2):
    server.start()
    client1.connect()
    client2.connect()    

    sent_messages = set()
    for i in range(20):
        msg = str(i).encode()        
        if i % 2 == 0:
            client1.send_message(msg)
        else:
            client2.send_message(msg)
        sent_messages.add(msg)

    received_messages1 = list()
    received_messages2 = list()    
    def cond(_):
        received_messages1.extend(client1.get_messages())
        received_messages2.extend(client2.get_messages())
        return received_messages1 == received_messages2 and set(received_messages1) == sent_messages
    assert loop_until_true(cond)
    

def test_detects_dead_server():
    server = ZmqServer(
        'tcp://*:5556',
        'tcp://*:5557',
        ping_interval=100
    )

    client = ZmqClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        tag='client',
        server_timeout=1        
    )
    
    server.start()
    client.connect()
    client.get_messages() # Pop initial control messages
    
    time.sleep(3)
    with pytest.raises(ConnectionLost):
        client.get_messages()
    server.stop()

    
def test_detects_stopped_server():
    server = ZmqServer(
        'tcp://*:5556',
        'tcp://*:5557',
        ping_interval=100
    )

    client = ZmqClient(
        'tcp://localhost:5556',
        'tcp://localhost:5557',
        tag='client',
        server_timeout=1        
    )
    
    server.start()
    client.connect()
    server.stop()
    
    with pytest.raises(ConnectionClosed):
        client.get_messages()
        
    

    

    
    

        
    
