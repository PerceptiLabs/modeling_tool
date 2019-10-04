import sys
import copy
import pprint
import logging
import numpy as np
import traceback
import tensorflow as tf

from core_new.ui import UiChannel
from core_new.api import Api, DataApi
from core_new.data import DataContainer, TrainValTestDataPolicy
from core_new.state import State
from core_new.utils import set_tensorflow_mode
from core_new.control import BaseControlApi, ControlApi
from core_new.results import ResultDictMaker
from core_new.session import LayerSession, LayerSessionStop
from core_new.execution import ExecutionScope

from graph import Graph


log = logging.getLogger(__name__)

class LayerScopeInitializer:
    """ Glues layers together by feeding the correct globals/locals """

    # TODO: maybe the contents of DataKeeper can be fed as default inputs to this one somehow?
    
    def __init__(self, default_globals=None, default_locals=None):
        self._global_outputs = {}
        self._local_outputs = {}
        self._default_globals = default_globals if default_globals is not None else {}

    def set_layer_outputs(self, id_, globals_, locals_):
        self._global_outputs[id_] = globals_
        self._local_outputs[id_] = locals_

    def get_layer_inputs(self, id_, input_layer_ids):
        locals_ = {'X': {}}
        globals_ = copy.copy(self._default_globals)
        
        if len(input_layer_ids) == 1:
            id_from = input_layer_ids[0]
            Y = self._local_outputs[id_from]['Y']
            locals_['X'] = {'Y': Y}
            globals_.update(self._global_outputs[id_from])
        elif len(input_layer_ids) > 1:
            locals_['X'] = {}
            for id_from in input_layer_ids:
                Y = self._local_outputs[id_from]['Y']
                locals_['X'][id_from] = {'Y': Y}
                globals_.update(self._global_outputs[id_from])

        return globals_, locals_

class SessionProcessHandler:
    def __init__(self, graph_dict, data_container, command_queue, result_queue, mode):
        self._graph = graph_dict
        self._data_container = data_container
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._mode = mode
        
    def on_process(self, session, dashboard):
        """ Called in response to 'api.ui.render' calls in the layer code """

        self._handle_commands(session)

        # Put data_container on result queue
        data_dict = self._data_container.to_dict()

        # Convert data container format to resultDict format.
        # TODO: maybe we want different policies for different dashboards in the future?
        data_policy = TrainValTestDataPolicy(session, data_dict, self._graph)
        results_dict = data_policy.get_results()
        self._result_queue.put(results_dict)
        
        if log.isEnabledFor(logging.DEBUG) and self._mode == 'normal':
            log.debug("Pushed results onto queue: " + str(results_dict))
        if log.isEnabledFor(logging.DEBUG) and self._mode == 'headless':            
            log.debug("Pushed results onto queue: " + pprint.pformat(results_dict, compact=True))
        
    def _handle_commands(self, session):
        while not self._command_queue.empty():
            command = self._command_queue.get()
            log.info("Received command '{}'".format(command))
        
            if command == 'pause':
                session.pause()
            elif command == 'run':
                session.unpause()
            elif command == 'stop':
                session.stop()
            else:
                log.warning("Unknown command: '{}'".format(command))        


class LayerExtrasReader:
    def __init__(self):
        self._dict = {}

    def to_dict(self):
        return copy.copy(self._dict)

    def read(self, session, data_container):
        shape = None
        Y = session.locals.get('Y')
        if isinstance(Y, tf.Tensor):
            shape = Y.shape.as_list()
        
        sample = None
        if session.layer_id in data_container:
            layer_dict = data_container[session.layer_id]
            
            if'sample' in layer_dict:
                sample = layer_dict['sample']
            
        self._dict[session.layer_id] = {'sample': sample, 'shape': shape}
        

class BaseCore:
    def __init__(self, codehq, graph_dict, data_container, session_process_handler=None, layer_extras_reader=None,
                 mode='normal', skip_layers=None, tf_eager=False):
        self._graph = graph_dict
        self._codehq = codehq
        self._mode = mode
        self._data_container = data_container
        self._tf_eager = tf_eager
        self._session_process_handler = session_process_handler
        self._layer_extras_reader = layer_extras_reader
        self._skip_layers = skip_layers if skip_layers is not None else []                
        
    def run(self):
        self._data_container.reset()

        if self._tf_eager:
            set_tensorflow_mode('eager')
        else:
            set_tensorflow_mode('graph') # Default to graph mode

        default_globals = {'tf': tf, 'np': np}
        scope_initializer = LayerScopeInitializer(default_globals) # Ensures layers have the correct input
        
        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]
            if layer_type in self._skip_layers:
                log.info("Skipping layer with id {} and type {}".format(layer_id, layer_type))
                continue

            log.info("Preparing layer session with id {} and type {}".format(layer_id, layer_type))
            try:
                self._run_layer(layer_id, content, scope_initializer)
            except LayerSessionStop:
                log.info("Stop requested during execution of layer session {}".format(layer_id))                
                break

        if self._tf_eager:
            set_tensorflow_mode('graph')        
            
    def _run_layer(self, id_, content, scope_initializer):
        code = self._codehq.get_code_generator(id_, content).get_code(mode=self._mode)            
        globals_, locals_ = scope_initializer.get_layer_inputs(id_, content["Con"])
            
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Session local variables [pre execution]: " + pprint.pformat(locals_, compact=True))
                
        session = LayerSession(id_,
                               code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler)                               
        try:        
            session.run() 
        except LayerSessionStop:
            raise # Not an error. Re-raise.
        except Exception as e:
            self._on_error(session, traceback.format_exc())
            raise
           
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Session local variables [post execution]: " + pprint.pformat(session.locals, compact=True))
            
        scope_initializer.set_layer_outputs(id_, session.globals, session.locals)

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.read(session, self._data_container)

    def on_error(self, session, formatted_exception):
        """ Handling of errors received when executing layer code """

        # Add line numbers to the code
        code_lines = session.code.split('\n')
        code_lines = ["%d %s" % (i, l) for i, l in enumerate(code_lines, 1)]
        code = "\n".join(code_lines)

        message  = "Exception when running layer session %s:\n" % session.layer_id
        message += "%s\n" % code
        message += "\n"
        message += formatted_exception
        log.error(message)

        # TODO: post message to error queue???


class Core(BaseCore):
    def __init__(self, codehq, graph_dict, data_container, session_process_handler, mode='normal'):
        super().__init__(codehq, graph_dict, data_container, session_process_handler=session_process_handler, mode=mode)

        
class LightweightCore(BaseCore):
    MODE = 'headless'    
    SKIP_LAYERS = ['TrainNormal']
    
    def __init__(self, codehq, graph_dict, data_container, layer_extras_reader):
        super().__init__(codehq, graph_dict, data_container, layer_extras_reader=layer_extras_reader, tf_eager=True,
                         skip_layers=self.SKIP_LAYERS, mode=self.MODE)

        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.DEBUG)

    import json
    import queue
    with open('net.json', 'r') as f:
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

    def f(queue, delay, command):
        time.sleep(delay)
        queue.put(command)

    import time
    import threading
    #threading.Thread(target=f, args=(cq, 4, 'pause')).start()
    #threading.Thread(target=f, args=(cq, 5, 'run')).start()    
    #threading.Thread(target=f, args=(cq, 8, 'stop')).start()        


    mode = 'headless'

    graph_dict = graph.graphs
    data_container = DataContainer()
    

    ler = LayerExtrasReader()

    lw_core = LightweightCore(CodeHq, graph_dict, data_container, ler)    
    lw_core.run()
    print(ler.to_dict())

    import pdb; pdb.set_trace()

    sph = SessionProcessHandler(graph_dict, data_container, cq, rq, mode)    
    core = Core(CodeHq, graph_dict, data_container, sph, mode=mode)
    core.run()

    

