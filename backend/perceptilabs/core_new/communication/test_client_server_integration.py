import os
import time
import pytest
import logging
from unittest.mock import MagicMock

from perceptilabs.utils import loop_until_true
from perceptilabs.core_new.utils import find_free_port
from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingClient, TrainingServer, State


log = logging.getLogger(__name__)


@pytest.fixture(scope='function', autouse=True)
def log_name():
    log.info(os.environ.get('PYTEST_CURRENT_TEST'))

    
def create_server(port1, port2, graph=None, snapshot_builder=None, userland_timeout=15):
    graph = graph or MagicMock()
    snapshot_builder = snapshot_builder or MagicMock()
    
    server = TrainingServer(
        port1, port2,
        graph,
        snapshot_builder=snapshot_builder,
        userland_timeout=userland_timeout
    )
    return server


def create_client(port1, port2, graph_builder=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=60):
    client = TrainingClient(
        port1, port2,
        graph_builder=graph_builder,
        on_receive_graph=on_receive_graph,
        on_log_message=on_log_message,
        on_userland_error=on_userland_error,
        on_userland_timeout=on_userland_timeout,
        on_server_timeout=on_server_timeout,
        server_timeout=server_timeout
    )
    return client

    
def test_receives_status_ready():
    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2)
    client = create_client(port1, port2)

    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()        
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.READY
        assert loop_until_true(cond)
    finally:
        server.shutdown()
        client.shutdown()


def test_receives_status_running_on_request_start():
    port1, port2 = find_free_port(count=2)
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_RUNNING
        assert loop_until_true(cond)
    finally:
        server.shutdown()
        client.shutdown()

        
def test_receives_status_paused_on_request():
    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert loop_until_true(cond)

        
    finally:
        server.shutdown()
        client.shutdown()
        

def test_can_resume_when_paused():
    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert loop_until_true(cond)

        client.request_resume()

        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_RUNNING
        assert loop_until_true(cond)
        
    finally:
        server.shutdown()
        client.shutdown()        


def test_receives_status_paused_on_request():
    port1, port2 = find_free_port(count=2)    
    server = create_server(port1, port2)
    client = create_client(port1, port2)
    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert loop_until_true(cond)

        
    finally:
        server.shutdown()
        client.shutdown()
        
        
def test_handles_received_graphs():
    snapshot = {'foo': 'bar'}
    snapshot_builder = MagicMock()
    snapshot_builder.build.return_value = snapshot
    
    graph_builder = MagicMock()
    on_receive_graph = MagicMock()

    def graph_run():
        while True:
            yield YieldLevel.SNAPSHOT

    graph = MagicMock()
    graph.run = graph_run

    port1, port2 = find_free_port(count=2)        
    server = create_server(port1, port2, graph, snapshot_builder=snapshot_builder)
    client = create_client(port1, port2, graph_builder=graph_builder, on_receive_graph=on_receive_graph)
    try:
        server_step = server.run_stepwise()
        client_step = client.run_stepwise()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return (
                graph_builder.build_from_snapshot.call_count == 1 and
                graph_builder.build_from_snapshot.call_args[0][0] == snapshot and 
                on_receive_graph.call_count == 1
            )
        assert loop_until_true(cond)

        
    finally:
        server.shutdown()
        client.shutdown()
        
        
