import os
import uuid
import time
import pytest
import logging
from unittest.mock import MagicMock

from perceptilabs.messaging.simple import SimpleMessageConsumer, SimpleMessageProducer, SimpleMessagingFactory
from perceptilabs.utils import loop_until_true
from perceptilabs.core_new.utils import find_free_port
from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingClient, TrainingServer, State


log = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def session_id():
    return uuid.uuid4().hex


@pytest.fixture(scope='function')
def topic_gn(session_id):
    topic_generic = f'generic-{session_id}'.encode()    
    return topic_generic


@pytest.fixture(scope='function')
def topic_sn(session_id):
    topic_snapshots = f'snapshots-{session_id}'.encode()
    return topic_snapshots


@pytest.fixture(scope='module')
def messaging_factory():
    return SimpleMessagingFactory()


@pytest.fixture
def consumer(messaging_factory, topic_gn, topic_sn):
    consumer = ZmqMessageConsumer([topic_gn, topic_sn])
    consumer.start()
    yield consumer
    consumer.stop()

    
@pytest.fixture
def producer(messaging_factory, topic_gn):
    producer = ZmqMessageProducer(topic_gn)
    producer.start()
    yield producer
    producer.stop()    

    
def create_server(messaging_factory, topic_gn, topic_sn, graph=None, snapshot_builder=None, userland_timeout=15):
    server_producer_generic = messaging_factory.make_producer(topic_gn)
    server_producer_snapshots = messaging_factory.make_producer(topic_sn)
    server_consumer = messaging_factory.make_consumer([topic_gn])

    graph = graph or MagicMock()
    snapshot_builder = snapshot_builder or MagicMock()
    
    server = TrainingServer(
        server_producer_generic, server_producer_snapshots, server_consumer,
        graph,
        snapshot_builder=snapshot_builder,
        userland_timeout=userland_timeout,
        max_time_run=120
    )
    return server


def create_client(messaging_factory, topic_gn, topic_sn, graph_builder=None, on_receive_graph=None, on_log_message=None, on_userland_error=None, on_userland_timeout=None, on_server_timeout=None, server_timeout=60):
    consumer = messaging_factory.make_consumer([topic_gn, topic_sn])
    producer = messaging_factory.make_producer(topic_gn)
    
    client = TrainingClient(
        producer, consumer,
        graph_builder=graph_builder,
        on_receive_graph=on_receive_graph,
        on_log_message=on_log_message,
        on_userland_error=on_userland_error,
        on_userland_timeout=on_userland_timeout,
        on_server_timeout=on_server_timeout,
        server_timeout=server_timeout
    )
    return client

    
def test_receives_status_ready(messaging_factory, topic_gn, topic_sn):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    client = create_client(messaging_factory, topic_gn, topic_sn)
    
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


def test_receives_status_running_on_request_start(messaging_factory, topic_gn, topic_sn):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    client = create_client(messaging_factory, topic_gn, topic_sn)
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

        
def test_receives_status_paused_on_request(messaging_factory, topic_gn, topic_sn):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    client = create_client(messaging_factory, topic_gn, topic_sn)    
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
        

def test_can_resume_when_paused(messaging_factory, topic_gn, topic_sn):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    client = create_client(messaging_factory, topic_gn, topic_sn)        
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


def test_handles_received_graphs(messaging_factory, topic_gn, topic_sn):
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

    server = create_server(messaging_factory, topic_gn, topic_sn, graph=graph, snapshot_builder=snapshot_builder)
    client = create_client(messaging_factory, topic_gn, topic_sn, graph_builder=graph_builder, on_receive_graph=on_receive_graph)    
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
        
        
