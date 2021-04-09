import logging
import copy
import time
import pprint
import logging
import threading
import numpy as np


from perceptilabs.messaging import MessagingFactory, ZmqMessagingFactory, SimpleMessagingFactory
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import NotReplicatedError


from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


PROCESS_COMMANDS_DELAY = 0.3
PROCESS_RESULTS_DELAY = 1.0


class CompatibilityCore:
    def __init__(self, command_queue, result_queue, graph_spec, trainer, threaded=False, model_id=None):
        self._model_id = model_id
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._graph_spec = graph_spec
        self._threaded = threaded
        self._running = False
        self._trainer = trainer
        
    def run(self):
        """ Runs the training """
        self._set_running(True)

        if self._threaded:
            self._run_trainer_threaded(self._trainer, self._graph_spec)
        else:
            self._run_trainer(self._trainer, self._graph_spec, on_iterate=[self._do_process_commands, self._do_process_results])

    def _run_trainer_threaded(self, trainer, graph_spec):
        """ Starts two workers: one for processing frontend commands, one for training """
        def worker(func, delay):
            logger.debug(f"Entering worker thread for function {func}. Period: {delay}")
            
            counter = 0
            while self.is_running and not self._trainer.is_closed:
                func(counter, self._trainer)
                counter += 1
                time.sleep(delay)
            func(counter, self._trainer)    #One extra for good measure

        threading.Thread(target=worker, args=(self._do_process_commands, PROCESS_COMMANDS_DELAY), daemon=True).start()    
        threading.Thread(target=worker, args=(self._do_process_results, PROCESS_RESULTS_DELAY), daemon=True).start()                  
        self._run_trainer(self._trainer, self._graph_spec)        

    def _run_trainer(self, trainer, graph_spec, on_iterate=None):
        try:
            trainer.run(self._graph_spec, on_iterate=on_iterate, model_id=self._model_id)
            logger.info("Trainer.run() called from CompatibilityCore")
        except:
            self._set_running(False)
            raise

    def _set_running(self, status):
        self._running = status
        logger.info(f"CompabilityCore is_running set to {status}")


    @property
    def is_running(self):
        return self._running        

    def _forward_command_to_trainer(self, trainer, command):
        if command.type == 'pause' and command.parameters['paused']:
            trainer.pause()
        elif command.type == 'pause' and not command.parameters['paused']:            
            trainer.unpause()
        elif command.type == 'stop':
            trainer.stop()
        elif command.type == 'close':
            trainer.close()
        elif command.type == 'headless' and command.parameters['on']:
            trainer.headless_on()
        elif command.type == 'headless' and not command.parameters['on']:            
            trainer.headless_off()
        elif command.type == 'export':
            trainer.export(command.parameters['path'], command.parameters['mode'])
        elif command.type == 'advance_testing':
            if hasattr(trainer, 'advance_testing'):
                trainer.advance_testing()
            else:
                logger.warning("Testing not implemented for current trainer")
            
    def _print_result_dict_debug_info(self, result_dict):
        if logger.isEnabledFor(logging.DEBUG):
            from perceptilabs.utils import stringify
            text = stringify(result_dict, indent=4, sort=True)
            logger.debug("result_dict: \n" + text)

    def _do_process_results(self, counter, trainer):
        """ Retrieves the resultDict from the Trainer """
        results = trainer.get_results()

        if results is not None:
            self._result_queue.queue.clear()
            self._result_queue.put(results)
            self._print_result_dict_debug_info(results)
        
    def _do_process_commands(self, counter, trainer):
        """ Process user commands coming in from the frontend (e.g., pause/unpause) """
        commands = {}
        count = {}

        while not self._trainer.is_ready:
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
                self._forward_command_to_trainer(trainer, command)
            except Exception as e:
                logger.exception(f'Error while processing command {command} in CompatibilityCore. Error is: {e}')
            

            

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
    core = CompatibilityCore(commandQ, resultQ, graph_builder, script_factory, messaging_factory, graph_spec, threaded=False)
    core.run()    
