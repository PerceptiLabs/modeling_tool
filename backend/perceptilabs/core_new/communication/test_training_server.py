import os
import time
import pytest
import logging
import threading
from unittest.mock import MagicMock

from perceptilabs.utils import loop_until_true
from perceptilabs.core_new.serialization import serialize, deserialize
from perceptilabs.core_new.communication import TrainingServer, TrainingClient, State
from perceptilabs.core_new.communication.zmq import ZmqClient
from perceptilabs.core_new.utils import find_free_port

log = logging.getLogger(__name__)


def create_server(port1, port2, graph=None, snapshot_builder=None, userland_timeout=15):
    graph = graph or MagicMock()
    snapshot_builder = snapshot_builder or MagicMock()
    
    server = TrainingServer(
        port1, port2,
        graph,
        snapshot_builder=snapshot_builder,
        userland_timeout=userland_timeout,
        max_time_run=120
    )
    return server


def create_client(port1, port2):
    client = ZmqClient(
        'tcp://localhost:{}'.format(port1),
        'tcp://localhost:{}'.format(port2)        
    )
    return client


def test_sends_state_ready():
    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': 'ready'} in messages

        assert loop_until_true(cond)
    finally:
        client.stop()
        server.shutdown()


def test_can_stop_when_ready():
    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_stop', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_STOPPED} in messages

        assert loop_until_true(cond) 
    finally:
        client.stop()
        server.shutdown()


def test_can_connect_before_server_and_receive_status_ready():
    port1, port2 = find_free_port(count=2)    
    try:
        keep_running = True
        def server_fn():
            time.sleep(2) # Wait for client to try to connect
            
            nonlocal keep_running
            server = create_server(port1, port2)
            step = server.run_stepwise()

            while keep_running:
                next(step)
                time.sleep(0.1)
                
            server.shutdown()
                

        server_thread = threading.Thread(target=server_fn)
        server_thread.start()
        
        client = create_client(port1, port2)            
        client.connect()

        def cond(_):
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_stop', 'value': ''}))
        
    finally:
        client.stop()
        
        keep_running = False
        server_thread.join()
        

def test_can_start_when_ready():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while True:
            n_training_steps_taken += 1
            yield
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)             
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_RUNNING} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken > 0
    finally:
        client.stop()
        server.shutdown()

        
def test_reaches_state_completed():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        for _ in range(10):
            n_training_steps_taken += 1
            yield
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)             
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_COMPLETED} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 10
    finally:
        client.stop()
        server.shutdown()

def test_userland_timeout_gives_timeout_state():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while n_training_steps_taken < 3:
            n_training_steps_taken += 1
            yield 0
        time.sleep(100)
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    
    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_TIMEOUT} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 3
    finally:
        client.stop()
        server.shutdown()


def test_userland_timeout_sends_timeout_message():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while n_training_steps_taken < 3:
            n_training_steps_taken += 1
            yield 0
        time.sleep(100)
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'userland-timeout', 'value': ''} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 3
    finally:
        client.stop()
        server.shutdown()
        
        
def test_userland_error_gives_error_state():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while n_training_steps_taken < 3:
            n_training_steps_taken += 1
            yield 0
        raise IndexError("Error!!")
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()

        def cond(_):
            next(step)             
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_FAILED} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 3
    finally:
        client.stop()
        server.shutdown()


def test_userland_error_sends_error_message():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while n_training_steps_taken < 3:
            n_training_steps_taken += 1
            yield 0
        raise IndexError("Error!!")
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()

        def cond(_):
            next(step)             
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]

            for m in messages:
                key = m.get('key')
                val = m.get('value')
                if key == 'userland-error' and isinstance(val['exception'], IndexError):
                    return True
            return False

        assert loop_until_true(cond)
        assert n_training_steps_taken == 3
    finally:
        client.stop()
        server.shutdown()
        

def test_can_pause():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while True:
            n_training_steps_taken += 1
            yield 0
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step) 
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        for i in range(5):
            next(step)

        client.send_message(serialize({'key': 'on_request_pause', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_PAUSED} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 5
    finally:
        client.stop()
        server.shutdown()

        
def test_can_resume_when_paused():
    n_training_steps_taken = 0
    
    def run_graph():
        nonlocal n_training_steps_taken
        while True:
            n_training_steps_taken += 1
            yield 0
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph, userland_timeout=1)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()    
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        next(step) 
        
        def cond(_):
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))

        for i in range(9):
            next(step)

        client.send_message(serialize({'key': 'on_request_pause', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_PAUSED} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken == 9

        for i in range(2):
            next(step)

        assert n_training_steps_taken == 9
        client.send_message(serialize({'key': 'on_request_resume', 'value': ''}))
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_RUNNING} in messages            

        assert loop_until_true(cond)
        assert n_training_steps_taken >= 10

            
    finally:
        client.stop()
        server.shutdown()
        
    
def test_calls_graph_stop_when_requested():
    graph = MagicMock()

    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)         
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_stop', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return graph.on_stop.call_count == 1

        assert loop_until_true(cond)
    finally:
        client.stop()
        server.shutdown()


def test_calls_graph_export_when_requested():
    graph = MagicMock()

    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        
        def cond(_):
            next(step)
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_export', 'value': {'path': 'abc', 'mode': 'xyz'}}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return (
                graph.on_export.call_count == 1 and
                graph.on_export.call_args_list[0][0][0] == 'abc' and
                graph.on_export.call_args_list[0][0][1] == 'xyz'
            )

        assert loop_until_true(cond)
    finally:
        client.stop()
        server.shutdown()


def test_calls_graph_headless_activate_when_requested():
    graph = MagicMock()

    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))        
        
        def cond(_):
            next(step)            
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_RUNNING} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_headless_activate', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return (
                graph.on_headless_activate.call_count == 1 and
                {'key': 'state', 'value': State.TRAINING_RUNNING_HEADLESS} in messages
            )

        assert loop_until_true(cond)
    finally:
        client.stop()
        server.shutdown()


def test_calls_graph_headless_deactivate_when_requested():
    graph = MagicMock()

    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2, graph)
    client = create_client(port1, port2)
    try:
        step = server.run_stepwise()
        
        next(step) # Initiates ZMQ and enters state ready
        client.connect()
        client.send_message(serialize({'key': 'on_request_start', 'value': ''}))
        client.send_message(serialize({'key': 'on_request_headless_activate', 'value': ''}))        
        
        def cond(_):
            next(step)            
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TRAINING_RUNNING_HEADLESS} in messages

        assert loop_until_true(cond)
        client.send_message(serialize({'key': 'on_request_headless_deactivate', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = client.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return (
                graph.on_headless_deactivate.call_count == 1 and
                {'key': 'state', 'value': State.TRAINING_RUNNING} in messages                
            )
                

        assert loop_until_true(cond)
    finally:
        client.stop()
        server.shutdown()
    
