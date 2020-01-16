import sys
import copy
import pprint
import logging
import numpy as np
import traceback
import tensorflow as tf
import pandas as pd
from collections import namedtuple
import gym

from graph import Graph
from modules import ModuleProvider
from core_new.api import Api, DataApi, UiApi
from core_new.data import DataContainer
from core_new.utils import set_tensorflow_mode
from core_new.extras import LayerExtrasReader
from core_new.errors import LayerSessionAbort
from core_new.history import SessionHistory, HistoryInputException
from core_new.session import LayerSession, LayerSessionStop, LayerIo
from core_new.data.policies import TrainValDataPolicy, TestDataPolicy, TrainReinforceDataPolicy
from analytics.scraper import get_scraper

log = logging.getLogger(__name__)
scraper = get_scraper()

class SessionProcessHandler:
    def __init__(self, graph_dict, data_container, command_queue, result_queue):  # mode
        self._graph = graph_dict
        self._data_container = data_container
        self._command_queue = command_queue
        self._result_queue = result_queue
        
    def on_process(self, session, dashboard):
        """ Called in response to 'api.ui.render' calls in the layer code """
        self._handle_commands(session)
        self._send_results(session, dashboard)
        
    def _send_results(self, session, dashboard):
        data_policy = self._get_data_policy(session, dashboard)
        results_dict = data_policy.get_results()
        
        self._result_queue.put(results_dict)
        # self._data_container.reset()
        #log.debug("Pushed results onto queue: " + pprint.pformat(results_dict, depth=2))
        
    def _handle_commands(self, session):
        while not self._command_queue.empty():
            command = self._command_queue.get()
            log.info("Received command '{}'".format(command))
            
            if command == 'pause':
                session.pause()
            elif command == 'unpause':
                session.unpause()
            elif command == 'run':
                session.unpause()
            elif command == 'stop':
                session.stop()
            elif command == 'headlessOn':
                session.headlessOn()
            elif command == 'headlessOff':
                session.headlessOff()
            elif command == "skip":
                session.skip = True
                
            else:
                log.warning("Unknown command: '{}'".format(command))        

    def _get_data_policy(self, session, dashboard):
        data_dict = self._data_container.to_dict()
        if dashboard == "train_val":
            data_policy = TrainValDataPolicy(session, data_dict, self._graph)
        elif dashboard == "testing":
            data_policy = TestDataPolicy(session, data_dict, self._graph)
        elif dashboard == "train_reinforce":
            data_policy = TrainReinforceDataPolicy(session, data_dict, self._graph)
        return data_policy

    
class BaseCore:    
    @scraper.monitor(tag='core_init')
    def __init__(self, codehq, graph_dict, data_container, session_history, module_provider, error_handler, session_process_handler=None,
                 layer_extras_reader=None, skip_layers=None, tf_eager=False, checkpointValues=None, network_cache=None): 
        self._graph = graph_dict
        self._codehq = codehq
        self._data_container = data_container
        self._tf_eager = tf_eager
        self._session_process_handler = session_process_handler
        self._error_handler = error_handler
        self._layer_extras_reader = layer_extras_reader
        self._session_history = session_history        
        self._skip_layers = skip_layers or []
        self._module_provider = module_provider
        self._checkpointValues = checkpointValues
        self._network_cache = network_cache

    def run(self):
        self._reset()        
        self._print_basic_info()
        
        set_tensorflow_mode('eager' if self._tf_eager else 'graph')

        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]

            if self._should_skip_layer(layer_id, content):
                continue

            if self._network_cache is not None:
                if layer_id in self._network_cache and not self._network_cache.needs_update(layer_id, content):
                    log.info("Using cached layer")
                    print("Using cached layer for layer " + layer_type)
                    self._use_cached_layer(layer_id, self._network_cache[layer_id])
                    continue
            print("***Calculating new layer for layer " + layer_type)
            log.info("Preparing layer session with id {} and type {}".format(layer_id, layer_type))
            try:
                self._run_layer(layer_id, content)
            except LayerSessionStop:
                log.info("Stop requested during session {}".format(layer_id))                
                break
            except LayerSessionAbort:
                
                log.info("Error handler aborted session {}".format(layer_id))
                break
            except Exception:
                log.exception("Exception in %s" % layer_id)
                raise

    def _run_layer(self, id_, content):        
        code_gen = self._codehq.get_code_generator(id_, content)
        log.debug(repr(code_gen))

        try:
            globals_, locals_ = self._get_globals_and_locals(input_layer_ids=content['Con'])  
        except HistoryInputException:
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.set_empty(id_)
                log.exception("HistoryInputException for layer %s" % content['Info']['Type'])
                return
            else:
                raise

        if content['Info']['checkpoint'] and type(code_gen).__name__ == "CustomCodeGenerator" and self._checkpointValues:
            locals_.update({"checkpoint":self._checkpointValues[content['Info']['checkpoint'][-1]]})
            code_gen.replace_ckpt_references()

        code = code_gen.get_code()

        session = LayerSession(id_, content['Info']['Type'], code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler,
                               cache=self._session_history.cache)   
        
        _save_cache=False

        try:        
            session.run()
        except LayerSessionStop:
            raise # Not an error. Re-raise.
        except Exception as e:
            self._error_handler.handle_run_error(session, e)
        # else:
        #     _save_cache=True

        self._session_history[id_] = session

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.read(session, self._data_container)

        if self._network_cache is not None:
            self._network_cache.update(id_, content, session, self._error_handler[id_] if id_ in self._error_handler.to_dict() else None)
            
        log.debug("Done running layer {}".format(id_))#. Locals:  {}".format(id_, session.outputs.locals))

    def _use_cached_layer(self, id_, saved_layer):
        if saved_layer.error:
            self._error_handler._dict[id_] = saved_layer.error

        if saved_layer.session._data_container[id_] is None:
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.set_empty(id_)
            return

        session = saved_layer.session

        self._session_history[id_] = session

        self._data_container.store_value_in_root(id_, saved_layer.session._data_container[id_])

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.read(session, self._data_container)
           
    def _get_globals_and_locals(self, input_layer_ids):
        input_layer_names = [self._graph[id_]['Info']['Name'] for id_ in input_layer_ids]
        outputs = self._session_history.merge_session_outputs(input_layer_ids, input_layer_names)
        # outputs = self._session_history.merge_session_outputs(input_layer_ids)

        # Load globals.
        # Note that modules imported via module provider will overwrite in-code imports        
        globals_ = {}
        globals_.update(outputs.globals) # Other global variables
        globals_.update(self._module_provider.modules) 

        # if log.isEnabledFor(logging.DEBUG): # TODO: remove this when done
        #     from code_generator.tensorflow import DummyEnv
        #     globals_['DummyEnv'] = DummyEnv
        
        locals_=outputs.locals

        return globals_, locals_
    
    def _reset(self):
        tf.reset_default_graph()
        self._data_container.reset()
        self._session_history.cache.invalidate(keep_layers=self._graph.keys())
        self._error_handler.reset()

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.clear()            

    def _print_basic_info(self):
        log.info("Running core [{}]".format(self.__class__.__name__))
        
        layer_repr = [id_ + ' [' + cont["Info"]["Type"]+']' for id_, cont in self._graph.items()]
        log.info("Layers will be executed in the following order: "+ ", ".join(layer_repr))
        
        if len(self._module_provider.hooks) > 0:
            targets = [x for x in self._module_provider.hooks.keys()]
            log.info("Module hooks installed are: {}".format(", ".join(targets)))
        else:
            log.info("No module hooks installed")

    def _should_skip_layer(self, layer_id, content):
        if not (content["Info"]["Properties"] \
                or ("Code" in content["Info"] and content["Info"]["Code"])):
            if self._layer_extras_reader is not None:
                return True
            else:
                raise Exception("Layer {} is empty and can therefore not run.\nMost likely it has not been properly Applied.".format(content["Info"]["Name"]))

        layer_type = content["Info"]["Type"]                
        if layer_type in self._skip_layers:
            log.info("Layer {} [{}] in skip list. Skipping.".format(layer_id, layer_type))
            return True
        
        return False

    @property
    def error_handler(self):
        return self._error_handler

class Core(BaseCore):
    def __init__(self, codehq, graph_dict, data_container, session_history,
                 module_provider, error_handler, session_process_handler, checkpointValues=None):
        super().__init__(codehq, graph_dict, data_container,
                         session_history, module_provider, error_handler,
                         session_process_handler=session_process_handler,
                         checkpointValues=checkpointValues)

        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.INFO)

    import json
    import queue
    import os
    os.environ['KMP_DUPLICATE_LIB_OK']='True'
    p1 = '/Users/mukund/Desktop/PerceptiLabs/backend/net.json'
    if os.path.exists(p1):
        path = p1
    else:
        path = 'net.json'
        
    
    with open(path, 'r') as f:
        json_network = json.load(f)

    graph = Graph(json_network["Layers"])

    from codehq import CodeHqNew as CodeHq

    #for id_, content in graph.graphs.items():
    #    code_gen = CodeHq.get_code_generator(id_, content)


    #gp = GraphPropagator(graph.graphs, CodeHq)
    #output = gp.propagate()


    
    #import pdb; pdb.set_trace()

    
    cq = queue.Queue()
    rq = queue.Queue()

    # def f(queue, delay, command):
    #     time.sleep(delay)
    #     queue.put(command)

    import time
    import threading
    #threading.Thread(target=f, args=(cq, 4, 'pause')).start()
    #threading.Thread(target=f, args=(cq, 5, 'run')).start()    
    #threading.Thread(target=f, args=(cq, 8, 'stop')).start()        


    # from core_new.lightweight import LightweightCore, placeholder_hook_1
    
    # module_provider = ModuleProvider()
    # module_provider.load('tensorflow', as_name='tf')
    # module_provider.load('numpy', as_name='np')

    # module_provider.install_hook('tf.placeholder', placeholder_hook_1, include_vars=True)


    graph_dict = graph.graphs
    data_container = DataContainer()
    
    # session_history = SessionHistory()
    # extras_reader = LayerExtrasReader()

    # lw_core = LightweightCore(CodeHq, graph_dict, data_container, 
    #                           session_history, module_provider, extras_reader)    
    # lw_core.run()
    # print(extras_reader.to_dict())

    # from newPropegateNetwork import newPropegateNetwork
    # newPropegateNetwork(json_network["Layers"])


    # def result_reader(q):
    #     # read and print whatever comes onto results queue
    #     while True:
    #         while not q.empty():
    #             res = q.get()
    #             import pprint
                
    #             print("RESULTS:" + pprint.pformat(res, depth=2))
    #         import time
    #         time.sleep(0.5)
        
    # threading.Thread(target=result_reader, args=(rq,)).start()            

    # # import pdb; pdb.set_trace()
    session_history = SessionHistory() 
   
    module_provider = ModuleProvider()
    module_provider.load('tensorflow', as_name='tf')
    module_provider.load('numpy', as_name='np')

    from core_new.errors import CoreErrorHandler
    import queue
    errorQueue=queue.Queue()
    error_handler = CoreErrorHandler(errorQueue)
   
    sph = SessionProcessHandler(graph_dict, data_container, cq, rq)    
    core = Core(CodeHq, graph_dict, data_container, session_history, module_provider, error_handler, sph)
    threading.Thread(target=core.run).start()