import logging
import copy
import time
import pprint
import logging
import threading
import numpy as np


from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.messaging import MessagingFactory, ZmqMessagingFactory, SimpleMessagingFactory
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import NotReplicatedError
from perceptilabs.core_new.compatibility.policies import policy_classification, policy_regression, policy_object_detection, policy_gan, policy_reinforce


from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


PROCESS_COMMANDS_DELAY = 0.3
PROCESS_RESULTS_DELAY = 0.1


class CompatibilityCore:
    def __init__(self, command_queue, result_queue, graph_builder, script_factory, messaging_factory, graph_spec, running_mode = 'training', threaded=False, issue_handler=None, model_id=None):
        self._model_id = model_id
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._graph_builder = graph_builder
        self._script_factory = script_factory
        self._messaging_factory = messaging_factory        
        self._graph_spec = copy.deepcopy(graph_spec)
        self._issue_handler = issue_handler
        self._running_mode = running_mode

        self._sanitized_to_id = {spec.sanitized_name: spec.id_ for spec in graph_spec.nodes}
        self._sanitized_to_name = {spec.sanitized_name: spec.name for spec in graph_spec.nodes}        

        self._threaded = threaded
        self._running = False
        self._core = None
        self.results = {}

    @property
    def core_v2(self):
        return self._core        
        
    def run(self):
        self._running = True

        def do_process_commands(counter, core): 
            commands = {}
            count = {}

            while not self._core.has_client:
                time.sleep(0.3)   
            
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
                    logger.debug(f'Processing command {command_id}: {command}. Overriding {count[command.type]-1} previous commands of the same type.') # TODO: logger.debug instead
                else:
                    logger.debug(f'Processing command {command_id}: {command}.') # TODO: logger.debug instead
                try:
                    self._send_command(core, command)
                except Exception as e:
                    logger.exception(f'Error while processing command {command} in CompatibilityCore. Error is: {e}')
            
        def do_process_results(counter, core):

            graphs = core.graphs

            if len(graphs) > 0:
                self.results = self._get_results_dicts(graphs, self.results)
                if self._running_mode == 'training':
                    self.results['training_duration'] = core.training_duration
                self._result_queue.put(copy.deepcopy(self.results))
            
        set_tensorflow_mode('graph')
        core = Core(self._graph_builder, self._script_factory, self._messaging_factory, self._issue_handler, running_mode = self._running_mode, use_sentry=True)
        self._core = core
        
        if self._threaded:
            def worker(func, delay):
                counter = 0
                while self._running and not self._core.is_closed:
                    func(counter, core)
                    counter += 1
                    time.sleep(delay)
                func(counter, core)    #One extra for good measure

            threading.Thread(target=worker, args=(do_process_commands, PROCESS_COMMANDS_DELAY), daemon=True).start()    
            threading.Thread(target=worker, args=(do_process_results, PROCESS_RESULTS_DELAY), daemon=True).start()                  
            self._run_core(core, self._graph_spec)
        else:
            self._run_core(core, self._graph_spec, on_iterate=[do_process_commands, do_process_results])            

    def _run_core(self, core, graph_spec, on_iterate=None):
        try:
            core.run(self._graph_spec, on_iterate=on_iterate, model_id=self._model_id)
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
        elif command.type == 'close':
            core.close()
        elif command.type == 'headless' and command.parameters['on']:
            core.headlessOn()
        elif command.type == 'headless' and not command.parameters['on']:            
            core.headlessOff()
        elif command.type == 'export':
            core.export(command.parameters['path'], command.parameters['mode'])
        elif command.type == 'advance_testing':
            core.advance_testing()            
            
    def _get_results_dicts(self, graphs, results):
        self._print_graph_debug_info(graphs)
        result_dicts = [{}]        
        try:
            result_dicts = self._get_results_dicts_internal(graphs, results)
        except:
            logger.exception('Error when getting results dict')
        finally:
            for result_dict in result_dicts:
                self._print_result_dict_debug_info(result_dict)
            return result_dicts                
    
    def _get_results_dicts_internal(self, graphs, results):
        if not graphs:
            logger.debug("graph is None, returning empty results")
            return [{}]
        layer = graphs[-1].active_training_node.layer
        if isinstance(layer, ClassificationLayer):
            result_dicts = policy_classification(self._core, graphs, self._sanitized_to_name, self._sanitized_to_id, results)
        elif  isinstance(layer, ObjectDetectionLayer):
            result_dicts = policy_object_detection(self._core, graphs, self._sanitized_to_name, self._sanitized_to_id, results)
        elif  isinstance(layer, GANLayer):
            result_dicts = policy_gan(self._core, graphs, self._sanitized_to_name, self._sanitized_to_id, results)
        elif  isinstance(layer, RegressionLayer):
            result_dicts = policy_regression(self._core, graphs, self._sanitized_to_name, self._sanitized_to_id, results)
        elif  isinstance(layer, RLLayer):
            result_dicts = policy_reinforce(self._core, graphs, self._sanitized_to_name, self._sanitized_to_id, results)
        return result_dicts

    def _print_graph_debug_info(self, graphs):
        if not logger.isEnabledFor(logging.DEBUG):
            return

        if len(graphs) == 0:
            logger.debug("No graphs available")
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

        logger.debug(text)

    def _print_result_dict_debug_info(self, result_dict):
        if logger.isEnabledFor(logging.DEBUG):
            from perceptilabs.utils import stringify
            text = stringify(result_dict, indent=4, sort=True)
            logger.debug("result_dict: \n" + text)
        


if __name__ == "__main__":

    import sys
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.DEBUG)
    
    import json
    import queue
    from perceptilabs.core_new.compatibility import CompatibilityCore
    from perceptilabs.core_new.graph.builder import GraphBuilder
    from perceptilabs.script import ScriptFactory
    from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP    
    from perceptilabs.graph.spec import GraphSpec
    from perceptilabs.utils  import patch_net_connections
    from perceptilabs.messaging import MessagingFactory, ZmqMessagingFactory, SimpleMessagingFactory
    
    with open('net.json', 'r') as f:
        network = json.load(f)
        
        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'TrainNormal' or layer['Type'] == 'Regression':
                layer['Properties']['Distributed'] = False

        network = network['Layers']
            
    script_factory = ScriptFactory(simple_message_bus=True)
    messaging_factory = SimpleMessagingFactory()
    
    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}    
    graph_builder = GraphBuilder(replica_by_name)                
    
    commandQ=queue.Queue()
    resultQ=queue.Queue()

    network = patch_net_connections(network)
    graph_spec = GraphSpec.from_dict(network)            

    import pdb; pdb.set_trace()
    
    core = CompatibilityCore(commandQ, resultQ, graph_builder, script_factory, messaging_factory, graph_spec, threaded=False)
    core.run()    
