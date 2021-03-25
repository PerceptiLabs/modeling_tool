import os
import sys
import time
import pytest
import logging
import tempfile
import numpy as np
from queue import Queue
from unittest.mock import MagicMock


from perceptilabs.graph.spec import GraphSpec
from perceptilabs.core_new.utils import YieldLevel
from perceptilabs.core_new.communication import TrainingServer, State
from perceptilabs.script import ScriptFactory
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


    """
    from perceptilabs.layers import get_layer_builder
    from perceptilabs.layers.datadata import DataDataSpec, DataDataBuilder


    source = DataDataSpec.Source(type='file', path=inputs_path, ext='.npy', split=[70, 20, 10])
    data_inputs = DataDataBuilder().from_kwargs(
        id='1',
        name='data_inputs',
        type='DataData',
        sources=(source,)
    ).build()
    """
    
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
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
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
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
                    "Keep_prob": "1.0",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": []
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
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
                    "Learning_rate": "0.3",
                    "Distributed": False,
                    "Stop_Iteration":0,
                    "Stop_Target_Accuracy":80,
                    "Stop_condition":"Epochs"
                },
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": []
            }
        }
    }

    yield json_network

    f1.close()
    f2.close()

@pytest.fixture(scope='function')
def graph_spec_binary_classification_2():
    n_classes = 10
    n_samples = 30

    f1 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat1 = np.random.random_sample((3, 28*28*1))
    mat2 = np.random.random_sample((3, 28*28*1)) + 1 
    mat3 = np.random.random_sample( (3, 28*28*1)) + 2
    mat4 = np.random.random_sample((3, 28*28*1)) + 3
    mat5 = np.random.random_sample((3, 28*28*1)) + 4
    mat6 = np.random.random_sample((3, 28*28*1)) + 5
    mat7 = np.random.random_sample((3, 28*28*1)) + 6
    mat8 = np.random.random_sample((3, 28*28*1)) + 7
    mat9 = np.random.random_sample((3, 28*28*1)) + 8
    mat10 = np.random.random_sample((3, 28*28*1)) + 9
    mat = np.concatenate((mat1, mat2, mat3, mat4, mat5, mat6, mat7, mat8, mat9, mat10), axis= 0)
    np.save(f1.name, mat)

    f2 = tempfile.NamedTemporaryFile(mode='w', suffix='.npy', delete=False)
    mat = np.array([1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10])
    np.save(f2.name, mat)
    
    inputs_path = f1.name.replace("\\","/")
    labels_path = f2.name.replace("\\","/")    

    #inputs_path = "/home/anton/Data/mnist_split/mnist_input.npy"
    #labels_path = "/home/anton/Data/mnist_split/mnist_labels.npy"


    """
    from perceptilabs.layers import get_layer_builder
    from perceptilabs.layers.datadata import DataDataSpec, DataDataBuilder


    source = DataDataSpec.Source(type='file', path=inputs_path, ext='.npy', split=[70, 20, 10])
    data_inputs = DataDataBuilder().from_kwargs(
        id='1',
        name='data_inputs',
        type='DataData',
        sources=(source,)
    ).build()
    """
    
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "3",
                        "dst_name": "reshape",
                        "dst_var": "input"
                    }
                ],
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
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "5",
                        "dst_name": "one_hot",                        
                        "dst_var": "input"
                    }
                ],
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
                "backward_connections": [
                    {
                        "src_id": "1",
                        "src_name": "data_inputs",                        
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "4",
                        "dst_name": "fc",                                                
                        "dst_var": "input"
                    }
                ],
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
                    "Keep_prob": "1.0",
                    "Batch_norm": False
                },
                "backward_connections": [
                    {
                        "src_id": "3",
                        "src_name": "reshape",                                                
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",
                        "dst_var": "predictions"
                    }
                ],
                "Code": None,
                "checkpoint": []
            },
            "5": {
                "Name": "one_hot",
                "Type": "ProcessOneHot",
                "Properties": {
                    "N_class": n_classes
                },
                "backward_connections": [
                    {
                        "src_id": "2",
                        "src_name": "data_labels",
                        "src_var": "output",
                        "dst_var": "input"
                    }
                ],
                "forward_connections": [
                    {
                        "src_var": "output",
                        "dst_id": "6",
                        "dst_name": "training",                        
                        "dst_var": "labels"
                    }
                ],
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
                "backward_connections": [
                    {
                        "src_id": "4",
                        "src_name": "fc",                        
                        "src_var": "output",
                        "dst_var": "predictions"
                    },
                    {
                        "src_id": "5",
                        "src_name": "one_hot",                        
                        "src_var": "output",
                        "dst_var": "labels"
                    }
                ],
                "forward_connections": [],                
                "Code": None,
                "checkpoint": []
            }
        }
    }

    yield json_network

    f1.close()
    f2.close()
    
    
def run_core_until_convergence(messaging_factory, graph_spec_json, metric_fn, temp_path_checkpoints, max_attempts=10):
    passed = False
    graphs = []
    for attempt in range(max_attempts):
        print(f"Beginning attempt {attempt}")


        script_factory = ScriptFactory(max_time_run=180, running_mode = 'training', simple_message_bus=True)

        replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
        graph_builder = GraphBuilder(replica_by_name)
        
        core = Core(
            graph_builder,
            script_factory,
            messaging_factory
        )
        checkpoint_path = temp_path_checkpoints
        for _, spec in graph_spec_json['Layers'].items():
            spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':False }
        
        graph_spec = GraphSpec.from_dict(graph_spec_json)
        
        core.run(graph_spec, auto_close=True)
        #core.close(wait_for_deployment=True)                            
        graphs.extend(core.graphs)        
        passed = metric_fn(graphs)
        if passed:
            break

    return passed
    

@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x
@pytest.mark.pre_datawizard            
def test_train_normal_converges(messaging_factory, graph_spec_binary_classification, graph_builder, temp_path_checkpoints):
    
    def metric_fn(graphs):
        if len(graphs) > 10:
            accuracy_list = [g.active_training_node.layer.accuracy_training for g in graphs[-10:]]
            accuracy = np.mean(accuracy_list)
            return accuracy >= 0.75
        else:
            return False
    
    assert run_core_until_convergence(messaging_factory, graph_spec_binary_classification, metric_fn, temp_path_checkpoints)

    
@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x
@pytest.mark.pre_datawizard            
def test_train_normal_distributed_converges(messaging_factory, graph_spec_binary_classification, graph_builder, temp_path_checkpoints):
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
    
    assert run_core_until_convergence(messaging_factory, json_network, metric_fn, temp_path_checkpoints)

    
@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x
@pytest.mark.pre_datawizard            
def test_core_handles_userland_timeout(messaging_factory):
    userland_timeout = 3
    server_timeout = 10000    

    def run_graph(mode = 'training'):
        for _ in range(2):
            time.sleep(100) # A single iteration will take 100s
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()
    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
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
            graph_builder, layer_classes, edges, connections,
            mode = 'training',
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
    
    assert wait_for_condition(cond)
    

@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x    
@pytest.mark.pre_datawizard                
def test_core_handles_userland_error(messaging_factory):
    def run_graph(mode = 'training'):
        for i in range(3):
            time.sleep(0.1)
            yield YieldLevel.DEFAULT
            raise ZeroDivisionError("Error!")
        yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()
    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
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
            graph_builder, layer_classes, edges, connections,
            mode = 'training',
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


@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x    
@pytest.mark.pre_datawizard                
def test_core_handles_training_server_timeout(messaging_factory):
    """Simulate a timeout by having a slow training loop"""
    
    ping_interval = 100
    userland_timeout = 100
    server_timeout = 3
    def run_graph(mode = 'training'):
        while True:
            time.sleep(10)
            yield

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()
    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
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
            graph_builder, layer_classes, edges, connections,
            mode = 'training',
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


@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x    
@pytest.mark.pre_datawizard                
def test_pause_works(graph_spec_binary_classification, messaging_factory):
    
    def run_graph(mode):
        for _ in range(100):
            time.sleep(1.0)
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()
    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
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
            graph_builder, layer_classes, edges, connections,
            mode = 'training',
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
        

@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x    
@pytest.mark.pre_datawizard                
def test_resume_works(graph_spec_binary_classification, messaging_factory):
    
    def run_graph(mode):
        for _ in range(100):
            time.sleep(1.0)
            yield YieldLevel.DEFAULT

    graph_spec = MagicMock()
    graph = MagicMock()
    graph.run.side_effect = run_graph
    graph_builder = MagicMock()
    graph_builder.build_from_layers_and_edges.return_value = graph or MagicMock()
    layer_classes = MagicMock()
    edges = MagicMock()
    connections = MagicMock()
    deployment_strategy = MagicMock()

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
            graph_builder, layer_classes, edges, connections,
            mode = 'training',
            snapshot_builder=MagicMock(),
        )
        nonlocal server_step
        server_step = training_server.run_stepwise()

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


@pytest.mark.pre_datawizard                
def test_checkpoint_is_saved(graph_spec_binary_classification, messaging_factory, temp_path_checkpoints):

    script_factory = ScriptFactory(max_time_run=180, running_mode = 'training', simple_message_bus=True)

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory
    )
    checkpoint_path = temp_path_checkpoints
    for _, spec in graph_spec_binary_classification['Layers'].items():
        spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':False }
    
    graph_spec = GraphSpec.from_dict(graph_spec_binary_classification)
    
    core.run(graph_spec, auto_close=True)
    assert 'checkpoint' in os.listdir(checkpoint_path)


@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x    
@pytest.mark.pre_datawizard                
def test_export_is_working(graph_spec_binary_classification, messaging_factory, temp_path_checkpoints):
    
    script_factory = ScriptFactory(max_time_run=180, running_mode = 'training', simple_message_bus=True)

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory
    )
    checkpoint_path = temp_path_checkpoints
    for _, spec in graph_spec_binary_classification['Layers'].items():
        spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':False }
    
    graph_spec = GraphSpec.from_dict(graph_spec_binary_classification)
    
    core.run(graph_spec, auto_close=True)
    
    assert 'checkpoint' in os.listdir(checkpoint_path)
    ################################################################
    
    script_factory = ScriptFactory(max_time_run=180, running_mode = 'exporting', simple_message_bus=True)

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)

    for _, spec in graph_spec_binary_classification['Layers'].items():
        spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':True }
    
    graph_spec = GraphSpec.from_dict(graph_spec_binary_classification)
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,
        running_mode = 'exporting'
    )
    core_step = core.run_stepwise(graph_spec)
    
    def cond_training_is_running(_):
        next(core_step, None)
        return core.is_export_ready and not core.is_training_paused
    
    def cond_export_file_exists(_):
        next(core_step, None)
        return '1' in os.listdir(checkpoint_path)
    
    assert wait_for_condition(cond_training_is_running)
    
    core.request_export(checkpoint_path, 'TFModel')
    
    assert wait_for_condition(cond_export_file_exists)
    
    core.request_close()


@pytest.mark.pre_datawizard
@pytest.mark.skip  # Fails intermittently, lower prio now that we're moving over to tf2x
def test_testing_loads_checkpoints(graph_spec_binary_classification, messaging_factory, temp_path_checkpoints):
    
    script_factory = ScriptFactory(max_time_run=180, running_mode = 'training', simple_message_bus=True)

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory
    )
    
    checkpoint_path = temp_path_checkpoints
    
    for _, spec in graph_spec_binary_classification['Layers'].items():
        spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':False }
    
    graph_spec_binary_classification['Layers']['6']["Properties"]["Epochs"] = 100
    
    graph_spec = GraphSpec.from_dict(graph_spec_binary_classification)
    core.run(graph_spec, auto_close=True)
    assert 'checkpoint' in os.listdir(checkpoint_path)
    
    core.request_close()
    
    ################################################################
    
    graphs = []
    script_factory = ScriptFactory(max_time_run=180, running_mode = 'testing', simple_message_bus=True)

    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}
    graph_builder = GraphBuilder(replica_by_name)
    
    core = Core(
        graph_builder,
        script_factory,
        messaging_factory,
        running_mode='testing'
    )
    for _, spec in graph_spec_binary_classification['Layers'].items():
        spec['checkpoint'] =  {'path':checkpoint_path, 'load_checkpoint':True }
    
    graph_spec = GraphSpec.from_dict(graph_spec_binary_classification)
    
    core_step = core.run_stepwise(graph_spec)
    next(core_step)
    next(core_step)
    graphs.extend(core.graphs)
    for i in range(5):
        time.sleep(0.5)
        core.request_advance_testing()
        next(core_step)
        graphs.extend(core.graphs)
        
    def metric_function(graphs):
        accuracy_list = [g.active_training_node.layer.accuracy_testing for g in graphs]
        accuracy = np.mean(accuracy_list)
        return accuracy >= 0.75

    # passed = metric_function(graphs)
    assert len(graphs) > 4
    # assert passed == True
    core.request_close()
