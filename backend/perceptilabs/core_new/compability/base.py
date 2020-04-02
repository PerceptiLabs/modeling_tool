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


PROCESS_COMMANDS_DELAY = 0.3
PROCESS_RESULTS_DELAY = 0.1


class CompabilityCore:
    def __init__(self, command_queue, result_queue, graph_builder, script_factory, graph_spec, threaded=False, issue_handler=None):
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._graph_spec = copy.deepcopy(graph_spec)
        self._issue_handler = issue_handler

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
        
        def do_process_commands(counter, core): 
            commands = {}
            count = {}
            
            while not self._command_queue.empty():
                command = self._command_queue.get()

                if command.type not in count:
                    count[command.type] = 0
                count[command.type] += 1

                if command.allow_override:
                    id_ = f'{command.type}-0'
                else:
                    id_ = f'{command.type}-{count[command.type]}'
                commands[id_] = command

            for command_id, command in commands.items():
                if command.allow_override and count[command.type] > 1:
                    log.debug(f'Processing command {command_id}: {command}. Overriding {count[command.type]-1} previous commands of the same type.') # TODO: log.debug instead
                else:
                    log.debug(f'Processing command {command_id}: {command}.') # TODO: log.debug instead
                self._send_command(core, command)
            
        def do_process_results(counter, core):
            graphs = core.graphs

            if len(graphs) > 0:
                log.debug(f"Processing {len(graphs)} graph snapshots")
                results = self._get_results_dict(graphs)
                self._result_queue.put(results)
            
        set_tensorflow_mode('graph')
        core = Core(self._graph_builder, self._script_factory, self._issue_handler)
        self._core = core
        
        if self._threaded:
            def worker(func, delay):
                counter = 0
                while self._running:
                    func(counter, core)
                    counter += 1
                    time.sleep(delay)
                func(counter, core)    #One extra for good measure

            threading.Thread(target=worker, args=(do_process_commands, PROCESS_COMMANDS_DELAY), daemon=True).start()    
            threading.Thread(target=worker, args=(do_process_results, PROCESS_RESULTS_DELAY), daemon=True).start()                  
            self._run_core(core, self._graph_spec)
        else:
            self._run_core(core, self._graph_spec, on_iterate=[do_process_commands, do_process_result])            

    def _run_core(self, core, graph_spec, on_iterate=None):
        try:
            core.run(self._graph_spec, on_iterate=on_iterate)
        except:
            self._running = False            
            raise     

    def _send_command(self, core, command):
        if command.type == 'pause' and command.parameters['paused']:
            core.pause()
        elif command.type == 'pause' and not command.parameters['paused']:            
            core.unpause()
        elif command.type == 'stop':
            core.stop()
        elif command.type == 'headless' and command.parameters['on']:
            core.headlessOn()
        elif command.type == 'headless' and not command.parameters['on']:            
            core.headlessOff()
        elif command.type == 'export':
            core.export(command.parameters['path'], command.parameters['mode'])            
            
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
        result_dict = policy_classification(self._core, graph, self._sanitized_to_name, self._sanitized_to_id)
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
    from perceptilabs.core_new.layers.script import ScriptFactory
    from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP    

    with open('net.json_', 'r') as f:
        network = json.load(f)

        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = False
        

    script_factory = ScriptFactory()
    
    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}    
    graph_builder = GraphBuilder(replica_by_name)                

    commandQ=queue.Queue()
    resultQ=queue.Queue()
    
    core = CompabilityCore(commandQ, resultQ, graph_builder, script_factory, network, threaded=False)
    core.run()
        
