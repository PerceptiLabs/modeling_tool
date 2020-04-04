import time
import pytest
from unittest.mock import MagicMock

from perceptilabs.utils import wait_for_condition
from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingClient, TrainingServer, State

    
def create_server(graph=None, snapshot_builder=None, step_timeout=15):
    graph = graph or MagicMock()
    snapshot_builder = snapshot_builder or MagicMock()
    
    server = TrainingServer(
        6556, 6557,
        graph,
        snapshot_builder=snapshot_builder,
        step_timeout=step_timeout
    )
    return server


def create_client(graph_builder=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=60):
    client = TrainingClient(
        6556, 6557,
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
    server = create_server()
    client = create_client()

    try:
        server_step = server.run_step()
        client_step = client.run_step()        
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.READY
        assert wait_for_condition(cond)
    finally:
        server.shutdown()
        client.shutdown()


def test_receives_status_running_on_request_start():
    server = create_server()
    client = create_client()
    try:
        server_step = server.run_step()
        client_step = client.run_step()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_RUNNING
        assert wait_for_condition(cond)
    finally:
        server.shutdown()
        client.shutdown()

        
def test_receives_status_paused_on_request():
    server = create_server()
    client = create_client()
    try:
        server_step = server.run_step()
        client_step = client.run_step()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert wait_for_condition(cond)

        
    finally:
        server.shutdown()
        client.shutdown()
        

def test_can_resume_when_paused():
    server = create_server()
    client = create_client()
    try:
        server_step = server.run_step()
        client_step = client.run_step()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert wait_for_condition(cond)

        client.request_resume()

        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_RUNNING
        assert wait_for_condition(cond)
        
    finally:
        server.shutdown()
        client.shutdown()        


def test_receives_status_paused_on_request():
    server = create_server()
    client = create_client()
    try:
        server_step = server.run_step()
        client_step = client.run_step()

        # Run one iteration for both to initiate the connection
        next(server_step)
        next(client_step)
        client.request_start()
        client.request_pause()
        
        def cond(_):
            next(server_step)
            next(client_step)
            return client.training_state == State.TRAINING_PAUSED
        assert wait_for_condition(cond)

        
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
    
    server = create_server(graph, snapshot_builder=snapshot_builder)
    client = create_client(graph_builder=graph_builder, on_receive_graph=on_receive_graph)
    try:
        server_step = server.run_step()
        client_step = client.run_step()

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
        assert wait_for_condition(cond)

        
    finally:
        server.shutdown()
        client.shutdown()
        
        
