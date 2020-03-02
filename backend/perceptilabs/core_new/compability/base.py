import copy
import time
import pprint
import logging
import threading
import numpy as np


from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import NotReplicatedError
from perceptilabs.core_new.compability.policies import policy_classification


log = logging.getLogger(__name__)


class CompabilityCore:
    def __init__(self, command_queue, result_queue, graph_builder, deployment_pipe, graph_spec, threaded=False, error_queue=None):
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._graph_spec = copy.deepcopy(graph_spec)
        self._error_queue = error_queue

        self._sanitized_to_id = {sanitize_layer_name(spec['Name']): id_ for id_, spec in graph_spec['Layers'].items()}
        self._sanitized_to_name = {sanitize_layer_name(spec['Name']): spec['Name'] for spec in graph_spec['Layers'].values()}        

        self._threaded = threaded
        self._running = False
        self._core = None

    @property
    def core_v2(self):
        return self._core        
        
    def run(self):
        self._running = True
        def do_process(counter, core):
            while not self._command_queue.empty():
                command = self._command_queue.get()
                self._send_command(core, command)

            graphs = core.graphs
            
            if len(graphs) > 0:
                log.debug(f"Processing {len(graphs)} graph snapshots")
                results = self._get_results_dict(graphs)
                self._result_queue.put(results)
            
        set_tensorflow_mode('graph')
        core = Core(self._graph_builder, self._deployment_pipe, self._error_queue)
        self._core = core
        
        if self._threaded:
            def worker():
                counter = 0
                while self._running:
                    do_process(counter, core)
                    counter += 1
                    time.sleep(1.0)
                do_process()    #One extra for good measure

            threading.Thread(target=worker, daemon=True).start()                    
            self._run_core(core, self._graph_spec)
        else:
            self._run_core(core, self._graph_spec, on_iterate=do_process)            

    def _run_core(self, core, graph_spec, on_iterate=None):
        try:
            core.run(self._graph_spec, on_iterate=on_iterate)
        except:
            self._running = False            
            raise     

    def _send_command(self, core, command):
        if command == 'pause':
            core.pause()
        elif command == 'unpause':
            core.unpause()
        elif command == 'stop':
            core.stop()
            
    def _get_results_dict(self, graphs):
        self._print_graph_debug_info(graphs)
        
        result_dict = {}        
        try:
            result_dict = self._get_results_dict_internal(graphs)
        except:
            log.exception('Error when getting results dict')
        finally:
            self._print_result_dict_debug_info(result_dict)
            return result_dict                
    
    def _get_results_dict_internal(self, graph):
        if not graph:
            log.debug("graph is None, returning empty results")
            return {}

        # TODO: if isinstance(training_layer, Classification) etc
        result_dict = policy_classification(graph, self._sanitized_to_name, self._sanitized_to_id)
        return result_dict

    def _print_graph_debug_info(self, graphs):
        if not log.isEnabledFor(logging.DEBUG):
            return

        if len(graphs) == 0:
            log.debug("No graphs available")
            return
        graph = graphs[-1]

        text = ""
        for node in graph.nodes:
            layer = node.layer
            attr_names = sorted(dir(layer))
            n_chars = max(len(n) for n in attr_names)
            
            text += f"{node.layer_id} [{type(layer.__class__.__name__)}]\n"
            for attr_name in attr_names:
                if hasattr(layer.__class__, attr_name) and isinstance(getattr(layer.__class__, attr_name), property):
                    name = attr_name.ljust(n_chars, ' ')
                    try:
                        value = getattr(layer, attr_name)
                        value_str = str(value).replace('\n', '')
                        if len(value_str) > 70:
                            value_str = value_str[0:70] + '...'
                        value_str = f'{value_str} [{type(value).__name__}]'
                    except NotReplicatedError:
                        value_str = '<not replicated>'
                    except Exception as e:
                        value_str = f'<error: {repr(e)}>'
                    finally:
                        text += f"    {name}: {value_str}\n"                        
            text += '\n'

        log.debug(text)

    def _print_result_dict_debug_info(self, result_dict):
        if log.isEnabledFor(logging.DEBUG):
            from perceptilabs.utils import stringify
            text = stringify(result_dict, indent=4, sort=True)
            log.debug("result_dict: \n" + text)
        


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.DEBUG)    
    import json
    import queue
    from perceptilabs.core_new.compability import CompabilityCore
    from perceptilabs.core_new.graph.builder import GraphBuilder
    from perceptilabs.core_new.deployment import InProcessDeploymentPipe, LocalEnvironmentPipe
    from perceptilabs.core_new.layers.script import ScriptFactory
    from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP    

    with open('net.json_', 'r') as f:
        network = json.load(f)

        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = False
        

    script_factory = ScriptFactory()
    deployment_pipe = InProcessDeploymentPipe(script_factory)
    #deployment_pipe = LocalEnvironmentPipe('/home/anton/Source/perceptilabs/backend/venv-user/bin/python', script_factory) # TODO: 
    
    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}    
    graph_builder = GraphBuilder(replica_by_name)                

    commandQ=queue.Queue()
    resultQ=queue.Queue()
    
    core = CompabilityCore(commandQ, resultQ, graph_builder, deployment_pipe, network, threaded=False)
    core.run()
        
