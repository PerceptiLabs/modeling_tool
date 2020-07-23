import os
import sys
import time
import pytest
import logging
import tempfile
import numpy as np
from queue import Queue
from unittest.mock import MagicMock


from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingServer, State
from perceptilabs.core_new.layers.script import ScriptFactory
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.graph.builder import GraphBuilder
from perceptilabs.core_new.graph import Graph
from perceptilabs.core_new.layers import TrainingSupervised, TrainingReinforce, TrainingRandom
from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP
from perceptilabs.utils import wait_for_condition
from perceptilabs.messaging.simple import SimpleMessageConsumer, SimpleMessageProducer, SimpleMessagingFactory


logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                    level=logging.DEBUG)


log = logging.getLogger(__name__)

@pytest.fixture
def graph_builder():
    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)    
    yield graph_builder


@pytest.fixture(scope='module')
def messaging_factory():
    return SimpleMessagingFactory()
    
    
@pytest.fixture(scope='function')
def graph_spec_binary_classification():
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.random((n_samples, 28*28*1))
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.random.randint(0, n_classes, (n_samples,))
    np.save(f2.name, mat)
    
    inputs_path = f1.name.replace("\\","/")
    labels_path = f2.name.replace("\\","/")    

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"
    
    json_network = {
        "Layers": {
            "1": {
                "Name": "data_inputs",
                "Type": "DataData",
                "Properties": {
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": inputs_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []                        
                    },
                },
                "backward_connections": [],
                "forward_connections": [["3", "reshape"]],
                "Code": None,
                "checkpoint": []
            },
            "2": {
                "Name": "data_labels",
                "Type": "DataData",
                "Properties": {
                    "Type": "DataData",
                    "accessProperties": {
                        "Sources": [{"type": "file", "path": labels_path}],
                        "Partition_list": [[70, 20, 10]],
                        "Shuffle_data": False,
                        "Columns": []
                    },
                },
                "backward_connections": [],
                "forward_connections": [["5", "one_hot"]],
                "Code": None,
                "checkpoint": []
            },
            "3": {
                "Name": "reshape",
                "Type": "ProcessReshape",                
                "Properties": {
                    "Shape": [28, 28, 1],
                    "Permutation": [0, 1, 2]
                },
                "backward_connections": [["1", "data_inputs"]],
                "forward_connections": [["4", "fc"]],
                "Code": None,
                "checkpoint": []
            },
            "4": {
                "Name": "fc",
                "Type": "DeepLearningFC",                
                "Properties": {
                    "Neurons": str(n_classes),
                    "Activation_function" : "Sigmoid",
                    "Dropout": False,
                    "Keep_prob": "1",
                    "Batch_norm": False
                },
                "backward_connections": [["3", "reshape"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [["2", "data_labels"]],
                "forward_connections": [["6", "training"]],
                "Code": None,
                "checkpoint": []
            },
            "6": {
                "Name": "training",
                "Type": "TrainNormal",
                "Properties": {
                    "Labels": "5",
                    "Loss": "Quadratic",
                    "Epochs": 50,
                    "Class_weights": "1",  # TODO: what's this?
                    "Optimizer": "SGD",
                    "Beta_1": "0.9",
                    "Beta_2": "0.999",
                    "Momentum": "0.9",
                    "Decay_steps": "100000",
                    "Decay_rate": "0.96",
                    "Batch_size": 10,                    
                    "Learning_rate": "0.05",
                    "Distributed": False,
                    "Stop_Iteration":0,
                    "Stop_Target_Accuracy":80,
                    "Stop_condition":"Epochs"
                },
                "backward_connections": [["4", "fc"], ["5", "one_hot"]],
                "forward_connections": [],
                "Code": None,
                "checkpoint": []
            }
        }
    }

    yield json_network

    f1.close()
    f2.close()


def run_core_until_convergence(messaging_factory, graph_spec, metric_fn, max_attempts=10):
    passed = False
    graphs = []
    for attempt in range(max_attempts):
        print(f"Beginning attempt {attempt}")
        script_factory = ScriptFactory(max_time_run=180, simple_message_bus=True)

        replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
        graph_builder = GraphBuilder(replica_by_name)
        
        core = Core(
            graph_builder,
            script_factory,
            messaging_factory
        )
        
        core.run(graph_spec, auto_close=True)
        #core.close(wait_for_deployment=True)                            
        graphs.extend(core.graphs)        
        passed = metric_fn(graphs)
        if passed:
            break

    return passed
    

@pytest.mark.slow
def test_train_normal_converges(messaging_factory, graph_spec_binary_classification, graph_builder):
    
    def metric_fn(graphs):
        if len(graphs) > 10:
            accuracy_list = [g.active_training_node.layer.accuracy_training for g in graphs[-10:]]
            accuracy = np.mean(accuracy_list)
            return accuracy >= 0.75
        else:
            return False
    
    assert run_core_until_convergence(messaging_factory, graph_spec_binary_classification, metric_fn)

    
@pytest.mark.slow
def test_train_normal_distributed_converges(messaging_factory, graph_spec_binary_classification, graph_builder):
    json_network = graph_spec_binary_classification
    json_network['Layers']['6']['Properties']['Distributed'] = True
    json_network['Layers']['6']['Properties']['Learning_rate'] = 0.1
    json_network['Layers']['6']['Properties']['Batch_size'] = 20


    def metric_fn(graphs):
        if len(graphs) > 10:
            accuracy_list = [g.active_training_node.layer.accuracy_training for g in graphs[-10:]]
            accuracy = np.mean(accuracy_list)
            return accuracy >= 0.75
        else:
            return False
    
    assert run_core_until_convergence(messaging_factory, json_network, metric_fn)

@pytest.mark.skip
def test_core_handles_userland_timeout(messaging_factory):
    userland_timeout = 3
    server_timeout = 10000    

    def run_graph():
        for _ in range(2):
            time.sleep(100) # A single iteration will take 100s
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    deployment_strategy = MagicMock()
    issue_handler = MagicMock()
    script_factory = MagicMock()
    script_factory.make.return_value = ('', {})


    server_step = None
    
    def run_deploy(path):
        topic_generic = script_factory.make.call_args[0][2]
        topic_snapshots = script_factory.make.call_args[0][3]
        
        prod_generic = messaging_factory.make_producer(topic_generic)
        prod_snapshots = messaging_factory.make_producer(topic_snapshots)
        consumer = messaging_factory.make_consumer([topic_generic])            

        training_server = TrainingServer(
            prod_generic, prod_snapshots, consumer,
            graph,
            snapshot_builder=MagicMock(),
            userland_timeout=userland_timeout,
            max_time_run=120
        )
        nonlocal server_step        
        server_step = training_server.run_stepwise()
    
    deployment_strategy.run.side_effect = run_deploy
    
    core = Core(
        graph_builder,
        script_factory,
        deployment_strategy=deployment_strategy,
        userland_timeout=userland_timeout,
        server_timeout=server_timeout,
        issue_handler=issue_handler
    )
    core_step = core.run_stepwise(graph_spec)

    def cond(_):
        next(core_step, None)
        next(server_step, None)
        return issue_handler.put_error.call_count == 1             
    
    assert wait_for_condition(cond)
    

def test_core_handles_userland_error(messaging_factory):
    def run_graph():
        for i in range(3):
            time.sleep(0.1)
            yield YieldLevel.DEFAULT
            raise ZeroDivisionError("Error!")
        yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    deployment_strategy = MagicMock()
    issue_handler = MagicMock()
    
    line_to_node_map = MagicMock()
    line_to_node_map.get.return_value = (MagicMock(), 123)
    script_factory = MagicMock()
    script_factory.make.return_value = ('', line_to_node_map)

    server_step = None
    def run_deploy(path):
        topic_generic = script_factory.make.call_args[0][2]
        topic_snapshots = script_factory.make.call_args[0][3]
        
        prod_generic = messaging_factory.make_producer(topic_generic)
        prod_snapshots = messaging_factory.make_producer(topic_snapshots)
        consumer = messaging_factory.make_consumer([topic_generic])            
        training_server = TrainingServer(
            prod_generic, prod_snapshots, consumer,                
            graph,
            snapshot_builder=MagicMock(),
            max_time_run=120                
        )
        nonlocal server_step
        server_step = training_server.run_stepwise()
    
    deployment_strategy.run.side_effect = run_deploy
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,
        deployment_strategy=deployment_strategy,
        issue_handler=issue_handler
    )

    core_step = core.run_stepwise(graph_spec)

    def cond(_):
        next(core_step, None)
        next(server_step, None)
        return issue_handler.put_error.call_count == 1
    
    assert wait_for_condition(cond)    
    
def test_core_handles_training_server_timeout(messaging_factory):
    """Simulate a timeout by having a slow training loop"""
    
    ping_interval = 100
    userland_timeout = 100
    server_timeout = 3
    def run_graph():
        while True:
            time.sleep(10)
            yield

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    deployment_strategy = MagicMock()
    script_factory = MagicMock()
    script_factory.make.return_value = ('', {})
    issue_handler = MagicMock()
    
    server_step = None
    def run_deploy(path):
        topic_generic = script_factory.make.call_args[0][2]
        topic_snapshots = script_factory.make.call_args[0][3]
        
        prod_generic = messaging_factory.make_producer(topic_generic)
        prod_snapshots = messaging_factory.make_producer(topic_snapshots)
        consumer = messaging_factory.make_consumer([topic_generic])            
        training_server = TrainingServer(
            prod_generic, prod_snapshots, consumer,                
            graph,
            snapshot_builder=MagicMock(),
            userland_timeout=userland_timeout,
            ping_interval=ping_interval,
            max_time_run=120                
        )
        nonlocal server_step
        server_step = training_server.run_stepwise()
            
    deployment_strategy.run.side_effect = run_deploy
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,        
        deployment_strategy=deployment_strategy,
        userland_timeout=userland_timeout,
        server_timeout=server_timeout,
        issue_handler=issue_handler
    )

    core_step = core.run_stepwise(graph_spec)

    def cond(_):
        next(core_step, None)
        next(server_step, None)
        return issue_handler.put_error.call_count == 1             
    
def test_pause_works(graph_spec_binary_classification, messaging_factory):
    
    def run_graph():
        for _ in range(100):
            time.sleep(1.0)
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()

    script_factory = MagicMock()
    script_factory.make.return_value = ('', {})


    server_step = None
    def run_deploy(path):
        topic_generic = script_factory.make.call_args[0][2]
        topic_snapshots = script_factory.make.call_args[0][3]
        
        prod_generic = messaging_factory.make_producer(topic_generic)
        prod_snapshots = messaging_factory.make_producer(topic_snapshots)
        consumer = messaging_factory.make_consumer([topic_generic])            
        training_server = TrainingServer(
            prod_generic, prod_snapshots, consumer,                
            graph,
            snapshot_builder=MagicMock(),
            max_time_run=120                
        )
        nonlocal server_step
        server_step = training_server.run_stepwise()

    deployment_strategy = MagicMock()    
    deployment_strategy.run.side_effect = run_deploy

    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,        
        deployment_strategy=deployment_strategy
    )

    core_step = core.run_stepwise(graph_spec)

    def cond_training_is_running(_):
        next(core_step, None)
        next(server_step, None)
        return core.is_training_running and not core.is_training_paused
    
    def cond_training_is_paused(_):
        next(core_step, None)
        next(server_step, None)
        return core.is_training_paused and not core.is_training_running

    
    assert wait_for_condition(cond_training_is_running)

    core.pause()    
    assert wait_for_condition(cond_training_is_paused)    
        
        
def test_resume_works(graph_spec_binary_classification, messaging_factory):
    
    def run_graph():
        for _ in range(100):
            time.sleep(1.0)
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()

    script_factory = MagicMock()
    script_factory.make.return_value = ('', {})


    server_step = None
    def run_deploy(path):
        topic_generic = script_factory.make.call_args[0][2]
        topic_snapshots = script_factory.make.call_args[0][3]
        
        prod_generic = messaging_factory.make_producer(topic_generic)
        prod_snapshots = messaging_factory.make_producer(topic_snapshots)
        consumer = messaging_factory.make_consumer([topic_generic])            
        training_server = TrainingServer(
            prod_generic, prod_snapshots, consumer,                
            graph,
            snapshot_builder=MagicMock(),
            max_time_run=120                
        )
        nonlocal server_step
        server_step = training_server.run_stepwise()

    deployment_strategy = MagicMock()    
    deployment_strategy.run.side_effect = run_deploy

    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,        
        deployment_strategy=deployment_strategy
    )

    core_step = core.run_stepwise(graph_spec)

    def cond_training_is_running(_):
        next(core_step, None)
        next(server_step, None)
        return core.is_training_running and not core.is_training_paused
    
    def cond_training_is_paused(_):
        next(core_step, None)
        next(server_step, None)
        return core.is_training_paused and not core.is_training_running

    
    assert wait_for_condition(cond_training_is_running)

    core.pause()    
    assert wait_for_condition(cond_training_is_paused)        

    core.unpause()    
    assert wait_for_condition(cond_training_is_running)        

    
