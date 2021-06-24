import os
import uuid
import time
import pytest
import logging
import threading
from unittest.mock import MagicMock


from perceptilabs.messaging.simple import SimpleMessageConsumer, SimpleMessageProducer, SimpleMessagingFactory
from perceptilabs.utils import loop_until_true
from perceptilabs.core_new.serialization import serialize, deserialize
from perceptilabs.core_new.communication import TrainingServer, TrainingClient, State
from perceptilabs.core_new.utils import find_free_port
from perceptilabs.core_new.utils import YieldLevel

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
def consumer(topic_gn, topic_sn, messaging_factory):
    consumer = messaging_factory.make_consumer([topic_gn, topic_sn])
    consumer.start()
    yield consumer
    consumer.stop()

    
@pytest.fixture
def producer(topic_gn, messaging_factory):
    producer = messaging_factory.make_producer(topic_gn)
    producer.start()
    yield producer
    producer.stop()    

    
def create_server(messaging_factory, topic_gn, topic_sn, graph=None, snapshot_builder=None, userland_timeout=15):
    server_producer_generic = messaging_factory.make_producer(topic_gn)
    server_producer_snapshots = messaging_factory.make_producer(topic_sn)
    server_consumer = messaging_factory.make_consumer([topic_gn])

    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()

    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
    
    snapshot_builder = snapshot_builder or MagicMock()
    
    server = TrainingServer(
        server_producer_generic, server_producer_snapshots, server_consumer,
        graph_builder,
        layer_classes,
        edges,
        connections,
        mode = 'testing',
        snapshot_builder=snapshot_builder,
        userland_timeout=userland_timeout,
        max_time_run=120
    )
    return server


@pytest.mark.skip
def test_sends_state_ready(messaging_factory, topic_gn, topic_sn, consumer):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    step = server.run_stepwise()

    try:
        def cond(_):
            next(step)
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': 'ready'} in messages
        
        assert loop_until_true(cond)
    finally:
        server.shutdown()


@pytest.mark.skip        
def test_can_stop_when_ready(messaging_factory, topic_gn, topic_sn, consumer, producer):
    server = create_server(messaging_factory, topic_gn, topic_sn)
    step = server.run_stepwise()
    try:
        step = server.run_stepwise()
        
        def cond(_):
            next(step)
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        producer.send(serialize({'key': 'on_request_stop', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TESTING_STOPPED} in messages

        assert loop_until_true(cond) 
    finally:
        server.shutdown()


@pytest.mark.skip        
def test_can_start_when_ready(messaging_factory, topic_gn, topic_sn, consumer, producer):
    n_training_steps_taken = 0
    
    def run_graph(mode = 'testing'):
        nonlocal n_training_steps_taken
        while True:
            n_training_steps_taken += 1
            print(n_training_steps_taken)
            yield
            
    graph = MagicMock()
    graph.run.side_effect = run_graph
    
    server = create_server(messaging_factory, topic_gn, topic_sn, graph=graph)    
    try:
        step = server.run_stepwise()
        
        def cond(_):
            next(step)             
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            print(messages)
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        producer.send(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            print(messages)            
            return {'key': 'state', 'value': State.TESTING_RUNNING} in messages

        assert loop_until_true(cond)
        assert n_training_steps_taken > 0
    finally:
        server.shutdown()
        

@pytest.mark.skip        
def test_state_changes_to_paused_after_iteration(messaging_factory, topic_gn, topic_sn, consumer, producer):
    n_testing_steps_to_take = 3
    n_snapshots_received = 0
    
    def run_graph(mode = 'testing'):
        for _ in range(n_testing_steps_to_take):
            yield YieldLevel.SNAPSHOT
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    snapshot_builder = MagicMock()
    snapshot_builder.build.return_value = {'key': 'value'}
    server = create_server(messaging_factory, topic_gn, topic_sn, graph=graph, snapshot_builder=snapshot_builder)        
    try:
        step = server.run_stepwise()
        
        def cond(_):
            next(step)             
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        producer.send(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            nonlocal n_snapshots_received
            next(step) # Keep iterating.
            
            raw_messages = consumer.get_messages()

            messages = []
            for raw_message in raw_messages:
                message = deserialize(raw_message)
                messages.append(message)
            return {'key': 'state', 'value': State.TESTING_PAUSED} in messages            

        assert loop_until_true(cond)
    finally:
        server.shutdown()


@pytest.mark.skip        
def test_can_resume_when_paused(messaging_factory, topic_gn, topic_sn, consumer, producer):
    n_training_steps_taken = 0
    
    def run_graph(mode = 'testing'):
        nonlocal n_training_steps_taken
        while True:
            n_training_steps_taken += 1
            yield 0
        yield 1
            
    graph = MagicMock()
    graph.run.side_effect = run_graph

    server = create_server(messaging_factory, topic_gn, topic_sn, graph, userland_timeout=1)
    try:
        step = server.run_stepwise()    
        
        def cond(_):
            next(step)             
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        producer.send(serialize({'key': 'on_request_start', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TESTING_PAUSED} in messages

        assert loop_until_true(cond)

        producer.send(serialize({'key': 'on_advance_testing', 'value': ''}))
        
        def cond(_):
            next(step)
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.TESTING_RUNNING} in messages            

        assert loop_until_true(cond)
            
    finally:
        server.shutdown()
        

@pytest.mark.skip        
def test_calls_graph_stop_when_requested(messaging_factory, topic_gn, topic_sn, consumer, producer):
    graph = MagicMock()

    server = create_server(messaging_factory, topic_gn, topic_sn, graph)
    try:
        step = server.run_stepwise()
        
        def cond(_):
            next(step)         
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return {'key': 'state', 'value': State.READY} in messages

        assert loop_until_true(cond)
        producer.send(serialize({'key': 'on_request_stop', 'value': ''}))

        def cond(_):
            next(step) # Keep iterating.
            raw_messages = consumer.get_messages()
            messages = [deserialize(m) for m in raw_messages]
            return graph.on_stop.call_count == 1

        assert loop_until_true(cond)
    finally:
        server.shutdown()

