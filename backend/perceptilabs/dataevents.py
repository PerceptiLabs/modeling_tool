from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER
import logging


logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)


def on_user_email_set():
    import pkg_resources
    import platform
    import psutil
    import GPUtil
    import time
    
    data_logger.info(
        'user_email_set',
        extra={
            'namespace': dict(
                cpu_count=psutil.cpu_count(),
                platform={
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'processor': platform.processor()
                },
                memory={
                    'phys_total': psutil.virtual_memory().total, # Deceptive naming, but OK according to docs: https://psutil.readthedocs.io/en/latest/
                    'phys_available': psutil.virtual_memory().available,
                    'swap_total': psutil.swap_memory().total,             
                    'swap_free': psutil.swap_memory().free
                },
                python={
                    'version': platform.python_version(),
                    'packages': [p.project_name + ' ' + p.version for p in pkg_resources.working_set]
                },
                gpus=[
                    {'name': gpu.name, 'driver': gpu.driver, 'memory_total': gpu.memoryTotal}
                    for gpu in GPUtil.getGPUs()
                ]
            )
        }
    )


def make_json_net_conform_to_schema(json_net):
    edges = []
    nodes = []
    for layer_spec in json_net.nodes:
        node = {
            'type': layer_spec.type_,
            'id': layer_spec.id_
        }
        
        namespace = {}
        if layer_spec.type_ == 'DataData':
            namespace['extensions'] = [s.ext for s in layer_spec.sources]
        if namespace:
            node['namespace'] = namespace

        nodes.append(node)
        
    return {
        'nodes': nodes,
        'edges': [list(e) for e in json_net.edges]
    }


def collect_start_metrics(json_net, graph, training_sess_id, model_id):
    """ quick-fix for collecting start metrics. update when newer version of core is merged"""
    import numpy as np

    n_params = 0
    # TODO: training layer parameter called n_parameters for proper generalization...
    for weights_dict in graph.active_training_node.layer.layer_weights.values():
        for w in weights_dict.values():
            n_params += np.prod(w.shape)

    for biases_dict in graph.active_training_node.layer.layer_biases.values():
        for b in biases_dict.values():
            n_params += np.prod(b.shape)

    formatted_graph = make_json_net_conform_to_schema(json_net)            
    
    data_logger.info(
        "training_started",
        extra={
            'namespace': dict(
                model_id=model_id,
                training_session_id=training_sess_id,        
                graph_spec=formatted_graph,
                n_parameters=int(n_params)
            )
        }
    )


def collect_end_metrics(json_net, graph, training_sess_id, session_info, model_id, end_state):
    """ quick-fix for collecting start metrics. update when newer version of core is merged"""
    import numpy as np

    n_params = 0
    # TODO: training layer parameter called n_parameters for proper generalization...
    for weights_dict in graph.active_training_node.layer.layer_weights.values():
        for w in weights_dict.values():
            n_params += np.prod(w.shape)

    for biases_dict in graph.active_training_node.layer.layer_biases.values():
        for b in biases_dict.values():
            n_params += np.prod(b.shape)

    formatted_graph = make_json_net_conform_to_schema(json_net)
    
    data_meta_list = []
    for node in graph.data_nodes:
        data_meta = {
            'layer_id': node.layer_id,
        }
        # TODO: remove hasattr when changes to DataLayer have been merged
        if node is not None and hasattr(node.layer, 'size_training'):
            data_meta.update({
                'training_set_size': int(node.layer.size_training),
                'validation_set_size': int(node.layer.size_validation),
                'testing_set_size': int(node.layer.size_testing),
                'sample_shape': list(node.layer.sample['output'].shape) if 'output' in node.layer.sample else []
            })
        data_meta_list.append(data_meta)

    data_logger.info(
        "training_ended",
        extra={
            'namespace': dict(
                model_id=model_id,
                training_session_id=training_sess_id,        
                n_parameters=int(n_params),
                time_total=session_info['time_total'],
                end_state=end_state,
                cycle_time_total=session_info['cycle_time_total'],
                mem_phys_total=session_info['mem_phys_total'],
                mem_swap_total=session_info['mem_swap_total'],
                cycle_time_process_messages=session_info['cycle_time_process_messages'],
                cycle_time_training_step=session_info['cycle_time_training_step'],
                cycle_time_send_snapshot=session_info['cycle_time_send_snapshot'],
                cycle_mem_phys_available=session_info['cycle_mem_phys_available'],
                cycle_mem_swap_free=session_info['cycle_mem_swap_free'],
                cycle_state_initial=session_info['cycle_state_initial'],
                cycle_state_final=session_info['cycle_state_final'],
                graph_spec=formatted_graph,
                data_meta=data_meta_list
            )
        }
    )


def collect_memory_limit_exceeded(max_memory_rate, core_interfaces):
    import pkg_resources
    import platform
    import psutil
    import GPUtil
    import time


    
    data_logger.info(
        "memory_limit_exceeded",
        extra={
            'namespace': dict(
                max_memory_rate=max_memory_rate,
                cpu_count=psutil.cpu_count(),
                platform={
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'processor': platform.processor()
                },
                memory={
                    'phys_total': psutil.virtual_memory().total, # Deceptive naming, but OK according to docs: https://psutil.readthedocs.io/en/latest/
                    'phys_available': psutil.virtual_memory().available,
                    'swap_total': psutil.swap_memory().total,             
                    'swap_free': psutil.swap_memory().free
                },
                gpus=[
                    {'name': gpu.name, 'driver': gpu.driver, 'memory_total': gpu.memoryTotal}
                    for gpu in GPUtil.getGPUs()
                ],
                core_interfaces=[
                    {
                        'running_mode': ci.running_mode or 'notset',
                        'training_session_id': ci.training_session_id or 'notset',
                        'training_state': ci.training_state or 'notset'
                    }
                    for ci in core_interfaces.values()
                ]                
            )
        }
    )


def collect_lwcore_finished(time_total, all_durations, has_cache):
    t_cache_lookup, t_compute, t_cache_insert, used_cache = [], [], [], []

    rnd = lambda x: float(round(x, 7))
    
    for durations in all_durations:
        t_cache_lookup.append(rnd(durations['t_cache_lookup']))
        t_compute.append(rnd(durations['t_compute']))
        t_cache_insert.append(rnd(durations['t_cache_insert']))
        used_cache.append(durations['used_cache'])
    
    data_logger.info(
        "lwcore_finished",
        extra={
            'namespace': {
                'time_total': time_total,                
                'has_cache': has_cache,
                't_cache_lookup': t_cache_lookup,
                't_compute': t_compute,
                't_cache_insert': t_cache_insert,
                'used_cache': used_cache                
            }
        }
    )
            

def collect_nth_iteration_ended(graph_spec, training_session_id, model_id, info):
    import numpy as np

    namespace = info
    namespace['training_layer_type'] = graph_spec.training_layer.type_
    namespace['training_session_id'] = training_session_id
    namespace['model_id'] = model_id
    
    data_logger.info(
        "nth_iteration_ended",
        extra={
            'namespace': namespace
        }
    )
