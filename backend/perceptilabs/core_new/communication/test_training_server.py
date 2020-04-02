from perceptilabs.core_new.communication import TrainingServer

'''
@pytest.fixture
def mock_graph_1s():
    def fn_run():
        for i in range(3):
            time.sleep(1)
            yield
    
    graph = MagicMock()
    graph.run.side_effect = fn_run
    yield

    
SERVERS = []

def create_server(graph, snapshot_builder=None):
    server = TrainingServer(
        7171, 7272
        graph=graph
        snapshot_builder=snapshot_builder
    )
    SERVERS.append(server)    
    return server


@pytest.fixture(autouse=True)
def shutdown_servers():
    for server in SERVERS:
        server.stop()
    SERVERS = []


def test_can_start_when_ready(mock_graph_1s):
    server = create_server(mock_graph_1s)
    step = server.start(threaded=False)

    next(step)
'''
    

    

    
    
