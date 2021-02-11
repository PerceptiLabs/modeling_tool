import time
import psutil
import asyncio
import logging
import numpy as np

import perceptilabs.dataevents as dataevents
from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)


MAX_MEMORY_RATE = 0.9 # warn the user if we exceed this limit
PERIOD_CHECK = 3.0 # How often the check will run


class MemoryWatcher:
    def __init__(self, issue_handler=None, core_interfaces=None):
        self._issue_handler = issue_handler
        self._core_interfaces = core_interfaces
        self._prev_usage = 0

    def initialize(self, event_loop: asyncio.BaseEventLoop):
        """ Adds the callback as a task on the event loop
        
        Args:
            event_loop: the event loop that will run the callback
        """
        self._task = event_loop.create_task(self._check_memory())
        return self._task

    def stop(self):
        self._task.cancel()

    async def _check_memory(self):
        """ Called repeatedly """
        while True:        
            try:        
                current_usage = self._get_memory_usage()                
                if current_usage >= MAX_MEMORY_RATE and self._prev_usage < MAX_MEMORY_RATE:
                    self._notify_user()
                    self._log_data()
                    self._log_to_console()
            except Exception as e:
                logger.exception("Error in memory watcher callback")
                    
            self._prev_usage = current_usage
            await asyncio.sleep(PERIOD_CHECK)

    def _get_memory_usage(self):
        """ Return the fraction of memory used """
        total_memory = psutil.virtual_memory().total # Deceptive naming (virtual memory), but OK according to docs: https://psutil.readthedocs.io/en/latest/
        available_memory = psutil.virtual_memory().available
        
        fraction_used = (total_memory-available_memory)/total_memory
        return fraction_used

    def _notify_user(self):
        if self._issue_handler:
            self._issue_handler.put_info("You are using a high amount of memory which may cause the tool to run slower than normally. For a smoother experience, try out our Docker version: https://perceptilabs.com/docs/quickstartguide")

    def _log_data(self):
        dataevents.collect_memory_limit_exceeded(MAX_MEMORY_RATE, self._core_interfaces)

    def _log_to_console(self):
        console_message = f"Memory usage exceeded {100*MAX_MEMORY_RATE}%! {len(self._core_interfaces)} active core interfaces."

        def estimate_weights_memory(training_layer):
            n_bytes = 0
            for weights_dict in training_layer.layer_weights.values():
                for w in weights_dict.values():
                    n_bytes += w.nbytes
            return n_bytes/(2**20)

        for counter, (receiver, core_interface) in enumerate(self._core_interfaces.items()):
            console_message += f"\n"
            console_message += f"  #{counter} Receiver: {receiver}\n"
            console_message += f"    network name: {core_interface.networkName}\n"
            console_message += f"    running mode: {core_interface.running_mode}\n"            
            console_message += f"    training state: {core_interface.training_state}\n"
            console_message += f"    training session id: {core_interface.training_session_id}"
            
            core = getattr(core_interface, 'core_v2', None)             
            if core is not None:
                console_message += f"\n    is_closed: {core.is_closed}"
                console_message += f"\n    is_closed_by_server: {core.is_closed_by_server}"

                if core.last_graph is not None and core.last_graph.active_training_node is not None:
                    training_node = core.last_graph.active_training_node
                    console_message += f"\n    training layer type: {type(training_node.layer)}"
                    
                    size = estimate_weights_memory(training_node.layer)
                    console_message += f"\n    est. weights size: {size} [MiB]"
                    
        logger.warning(console_message)

    




    
        

