import time
import pytest
from unittest.mock import MagicMock

from perceptilabs.utils import wait_for_condition
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
def mock_graph_2s_error():
    def fn_run():
        time.sleep(1)
        yield
        if True:
            raise IndexError("Index is bad!")
        yield

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

@pytest.fixture
def mock_graph_infinite_loop():
    def fn_run():
        while True:
            time.sleep(1)
        yield
    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield graph


SERVERS = []
CLIENTS = []


def create_server(graph, snapshot_builder=None, max_step_time=60):
    server = TrainingServer(
        6556, 6557,
        graph,
        snapshot_builder=snapshot_builder,
        max_step_time=max_step_time
    )
    SERVERS.append(server)    
    return server


def create_client(graph_builder=None, on_userland_error=None, max_response_time=10):
    client = TrainingClient(
        6556, 6557,
        graph_builder=graph_builder,
        on_userland_error=on_userland_error,
        max_response_time=max_response_time
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

    
def test_can_connect(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()

    server.start()
    client.connect()

    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    

def test_can_start(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()

    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)

    
def test_can_start_10_times(mock_graph_3s):
    for i in range(10):
        print(f"Attempt {i}")    
        server = create_server(mock_graph_3s)
        client = create_client()

        server.start()
        client.connect()
        assert wait_for_condition(lambda _: client.remote_status == State.READY)
        
        client.request_start()
        assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)

        client.stop()
        server.stop()


def test_can_stop_when_ready(mock_graph_3s):
    print("CAN STOP WHEN READY")
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_stop()
    assert wait_for_condition(lambda _: client.remote_status == State.DONE)


def test_can_stop_when_running(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)

    client.request_stop()
    assert wait_for_condition(lambda _: client.remote_status == State.DONE)


def test_can_pause_when_running(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()

    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)

    client.request_pause()
    assert wait_for_condition(lambda _: client.remote_status == State.PAUSED)
    

def test_can_stop_when_paused(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)


    client.request_pause()
    assert wait_for_condition(lambda _: client.remote_status == State.PAUSED)

    client.request_stop()
    assert wait_for_condition(lambda _: client.remote_status == State.DONE)


def test_can_resume_when_paused(mock_graph_3s):
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)

    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)

    client.request_pause()
    assert wait_for_condition(lambda _: client.remote_status == State.PAUSED)

    client.request_resume()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)


def test_can_stop_when_idle(mock_graph_1s):
    server = create_server(mock_graph_1s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.IDLE)

    client.request_stop()
    assert wait_for_condition(lambda _: client.remote_status == State.DONE)

    
def test_receives_3_graphs_and_goes_idle(mock_graph_3s_with_snapshot):
    snapshot_builder = MagicMock()
    snapshot_builder.build.return_value = {'foo': 'bar'}

    graph_builder = MagicMock()
    graph_builder.build_from_snapshot.return_value = object()
    
    server = create_server(mock_graph_3s_with_snapshot, snapshot_builder=snapshot_builder)
    client = create_client(graph_builder=graph_builder)
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.RUNNING)
    
    assert wait_for_condition(lambda _: client.remote_status == State.IDLE)
    assert wait_for_condition(lambda _: len(client.graphs) == 3)


def test_stops_on_userland_error(mock_graph_2s_error):
    server = create_server(mock_graph_2s_error)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == State.DONE)

    
def test_sends_message_on_userland_error(mock_graph_2s_error):
    fn = MagicMock()
    
    server = create_server(mock_graph_2s_error)
    client = create_client(on_userland_error=fn)
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: fn.call_count == 1)


def test_layer_export_called(mock_graph_3s):
    fn = MagicMock()
    
    server = create_server(mock_graph_3s)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_export(path='/hello/', mode='some-mode')

    assert wait_for_condition(lambda _: mock_graph_3s.active_training_layer.layer.on_export.call_count == 1)
    assert wait_for_condition(lambda _: mock_graph_3s.active_training_layer.layer.on_export.call_args_list[0][0][0] == '/hello/')
    assert wait_for_condition(lambda _: mock_graph_3s.active_training_layer.layer.on_export.call_args_list[0][0][1] == 'some-mode')

    
def test_stops_on_userland_timeout(mock_graph_infinite_loop):
    server = create_server(mock_graph_infinite_loop, max_step_time=5)
    client = create_client()
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: client.remote_status == None)

def test_client_stops_on_server_timeout(mock_graph_infinite_loop):
    server = create_server(mock_graph_infinite_loop, max_step_time=60)
    client = create_client(max_response_time=3)
    
    server.start()
    client.connect()
    assert wait_for_condition(lambda _: client.remote_status == State.READY)
    
    client.request_start()
    assert wait_for_condition(lambda _: not client.is_running)
    
    

    
    

    

    
