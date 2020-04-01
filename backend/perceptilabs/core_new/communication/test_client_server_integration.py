import time
import pytest
from unittest.mock import MagicMock

from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingClient, TrainingServer, State

@pytest.fixture
def mock_graph_1s():
    def fn_run():
        for i in range(1):
            time.sleep(1)
            yield YieldLevel.DEFAULT
    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield graph

@pytest.fixture
def mock_graph_3s_with_snapshot():
    def fn_run():
        for i in range(3):
            time.sleep(1)
            yield YieldLevel.SNAPSHOT
    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield graph
    

@pytest.fixture
def mock_graph_3s():
    def fn_run():
        for i in range(3):
            time.sleep(1)
            yield YieldLevel.DEFAULT            

    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield graph


@pytest.fixture
def mock_graph_5s():
    def fn_run():
        for i in range(5):
            time.sleep(1)
            yield YieldLevel.DEFAULT                        
    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield graph

    
SERVERS = []
CLIENTS = []

def create_server(graph, snapshot_builder=None):
    server = TrainingServer(
        6556, 6557,
        graph,
        snapshot_builder=snapshot_builder
    )
    SERVERS.append(server)    
    return server


def create_client(graph_builder=None):
    client = TrainingClient(6556, 6557, graph_builder=graph_builder)
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


def test_can_connect(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()

    server.start()
    client.connect()
    time.sleep(1.0)

    assert client.remote_status == State.READY
    

def test_can_start(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()

    server.start()
    client.connect()
    time.sleep(1.0)

    assert client.remote_status == State.READY
    
    client.request_start()
    time.sleep(1.0)

    assert client.remote_status == State.RUNNING

    
def test_can_start_10_times(mock_graph_3s):
    for i in range(10):
        print(f"Attempt {i}")    
        server = create_server(mock_graph_3s)
        client = create_client()

        server.start()
        client.connect()
        time.sleep(0.3)

        assert client.remote_status == State.READY
        
        client.request_start()
        time.sleep(0.3)

        assert client.remote_status == State.RUNNING

        client.stop()
        server.stop()


def test_can_stop_when_ready(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)
    
    assert client.remote_status == State.READY
    client.request_stop()
    time.sleep(0.3)
    
    assert client.remote_status == State.DONE


def test_can_stop_when_running(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)
    
    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(0.3)
    
    assert client.remote_status == State.RUNNING

    client.request_stop()
    time.sleep(1.3) 
    
    assert client.remote_status == State.DONE


def test_can_pause_when_running(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)
    
    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(0.3)
    
    assert client.remote_status == State.RUNNING

    client.request_pause()
    time.sleep(1.3)
    
    assert client.remote_status == State.PAUSED


def test_can_stop_when_paused(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)

    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(0.3)
    
    assert client.remote_status == State.RUNNING

    client.request_pause()
    time.sleep(1.3)
    
    assert client.remote_status == State.PAUSED

    client.request_stop()
    time.sleep(0.3)
    
    assert client.remote_status == State.DONE


def test_can_resume_when_paused(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)    

    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(0.3)
    
    assert client.remote_status == State.RUNNING

    client.request_pause()
    time.sleep(1.3)
    
    assert client.remote_status == State.PAUSED

    client.request_resume()
    time.sleep(0.3)
    
    assert client.remote_status == State.RUNNING


def test_can_stop_when_idle(mock_graph_1s):
    server = create_server(mock_graph_1s)
    client = create_client()
    
    server.start()
    client.connect()
    time.sleep(0.3)

    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(2.0)

    assert client.remote_status == State.IDLE

    client.request_stop()
    time.sleep(0.3)    

    assert client.remote_status == State.DONE

    
def test_receives_3_graphs_and_goes_idle(mock_graph_3s_with_snapshot):
    snapshot_builder = MagicMock()
    snapshot_builder.build.return_value = {'foo': 'bar'}

    graph_builder = MagicMock()
    graph_builder.build_from_snapshot.return_value = object()
    
    server = create_server(mock_graph_3s_with_snapshot, snapshot_builder=snapshot_builder)
    client = create_client(graph_builder=graph_builder)
    
    server.start()
    client.connect()
    time.sleep(0.3)
    
    assert client.remote_status == State.READY
    client.request_start()
    time.sleep(1.0)
    
    assert client.remote_status == State.RUNNING
    time.sleep(3.0)

    assert client.remote_status == State.IDLE    
    assert len(client.graphs) == 3




    
    

    

    
