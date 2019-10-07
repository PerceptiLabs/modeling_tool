import sys
import copy
import pprint
import logging
import numpy as np
import traceback
import tensorflow as tf


from core_new.api import Api, DataApi, UiApi
from core_new.data import DataContainer, TrainValTestDataPolicy
from core_new.utils import set_tensorflow_mode
from core_new.session import LayerSession, LayerSessionStop

from graph import Graph


log = logging.getLogger(__name__)


class SessionHistory:
    def __init__(self):
        self.reset()

    def reset(self):
        self._sessions = {}        

    def __contains__(self, id_):
        return id_ in self._sessions
        
    def __setitem__(self, id_, value):
        self._sessions[id_] = value

    def items(self):
        for id_, session in self._sessions.items():
            yield id_, session

    def merge_session_outputs(self, layer_ids):
        results = {}
        if len(layer_ids) == 1:
            print(layer_ids)
            session = self._sessions[layer_ids[0]]
            results.update(session.outputs)
        elif len(layer_ids) > 1:
            for id_ in layer_ids:
                session = self._sessions[id_]                
                results[id_] = session.outputs
                
        return results

    
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
        self._send_results(session)
        
    def _send_results(self, session):
        data_dict = self._data_container.to_dict()
        data_policy = TrainValTestDataPolicy(session, data_dict, self._graph) # Convert data container format to resultDict format.
        
        results_dict = data_policy.get_results()
        self._result_queue.put(results_dict)
        log.debug("Pushed results onto queue: " + pprint.pformat(results_dict, depth=1))
        
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

    def _put_in_dict(self, key, value):
        try:
            self._dict[key].update(value)
        except:
            self._dict[key]=value

    def _evalSample(self,sample):
        if isinstance(sample, tf.Tensor) or isinstance(sample, tf.Variable):
            return sample.numpy()
        else:
            return sample

    def read(self, session, data_container):
        shape = ''
        Y = session.locals.get('Y')
        if isinstance(Y, tf.Tensor):
            shape = Y.shape.as_list()
            if not shape:
                shape=[1]
        
        sample = ''
        if session.layer_id in data_container:
            layer_dict = data_container[session.layer_id]
            
            if 'sample' in layer_dict:
                sample = layer_dict['sample']
            elif 'Y' in layer_dict:
                sample = layer_dict['Y']

        sample=self._evalSample(sample)
        self._put_in_dict(session.layer_id,{'sample': sample,'shape': shape})

    def read_syntax_error(self, session):
        tbObj=traceback.TracebackException(*sys.exc_info())
        self._put_in_dict(session.layer_id,{"errorMessage": "".join(tbObj.format_exception_only()), "errorRow": tbObj.lineno or "?"})    

    def read_error(self, session, e):
        error_class = e.__class__.__name__
        detail = e
        _, _, tb = sys.exc_info()
        tb_list=traceback.extract_tb(tb)
        line_number=""
        for i in tb_list:
            if i[2]=="<module>":
                line_number=i[1]

        if line_number=="":
            line_number = tb.tb_lineno

        self._put_in_dict(session.layer_id, {"errorMessage": "%s at line %d: %s" % (error_class, line_number, detail), "errorRow": line_number})
    

class BaseCore:
    def __init__(self, codehq, graph_dict, data_container, session_history, session_process_handler=None,
                 layer_extras_reader=None, mode='normal', skip_layers=None, tf_eager=False):
        self._graph = graph_dict
        self._codehq = codehq
        self._mode = mode
        self._data_container = data_container
        self._tf_eager = tf_eager
        self._session_process_handler = session_process_handler
        self._layer_extras_reader = layer_extras_reader
        self._session_history = session_history        
        self._skip_layers = skip_layers if skip_layers is not None else []        

        
    def run(self):
        self._data_container.reset()

        if self._tf_eager:
            set_tensorflow_mode('eager')
        else:
            set_tensorflow_mode('graph') # Default to graph mode

        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]
            if layer_type in self._skip_layers:
                log.info("Layer {} [{}] in skip list. Skipping.".format(layer_id, layer_type))
                continue

            if layer_id in self._session_history:
                log.info("Layer {} [{}] already in history. Skipping.".format(layer_id, layer_type))
                continue

            log.info("Preparing layer session with id {} and type {}".format(layer_id, layer_type))
            try:
                self._run_layer(layer_id, content)
            except LayerSessionStop:
                log.info("Stop requested during execution of layer session {}".format(layer_id))                
                break

        if self._tf_eager:
            set_tensorflow_mode('graph')        
            
    def _run_layer(self, id_, content):
        
        code = self._codehq.get_code_generator(id_, content).get_code(mode=self._mode)            
        #globals_, locals_ = scope_initializer.get_layer_inputs(id_, content["Con"])
            
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Session local variables [pre execution]: " + pprint.pformat(locals_, compact=True))

        globals_ = {'tf': tf, 'np': np}
        locals_ = {'X': self._session_history.merge_session_outputs(content['Con'])}
                
        session = LayerSession(id_, content['Info']['Type'], code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler)                               
        try:        
            session.run() 
        except LayerSessionStop:
            raise # Not an error. Re-raise.
        except SyntaxError as e:
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.read_syntax_error(session)
            else:
                raise
        except Exception as e:
            # self._on_error(session, traceback.format_exc())
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.read_error(session,e)
            else:
                raise
        
           
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Session local variables [post execution]: " + pprint.pformat(session.locals, compact=True))
            
        self._session_history[id_] = session

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
    def __init__(self, codehq, graph_dict, data_container, session_history,
                 session_process_handler, mode='normal'):
        super().__init__(codehq, graph_dict, data_container, session_history,
                         session_process_handler=session_process_handler, mode=mode)

        
class LightweightCore(BaseCore):
    MODE = 'headless'    
    SKIP_LAYERS = ['TrainNormal']
    
    def __init__(self, codehq, graph_dict, data_container, session_history, layer_extras_reader):
        super().__init__(codehq, graph_dict, data_container, session_history,
                         layer_extras_reader=layer_extras_reader, tf_eager=True,
                         skip_layers=self.SKIP_LAYERS, mode=self.MODE)

        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.INFO)

    import json
    import queue
    import os

    p1 = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Networks/net.json'
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




    graph_dict = graph.graphs
    data_container = DataContainer()
    
    session_history_lw = SessionHistory()
    extras_reader = LayerExtrasReader()

    lw_core = LightweightCore(CodeHq, graph_dict, data_container, 
                              session_history_lw, extras_reader)    
    lw_core.run()
    print(extras_reader.to_dict())

    # from newPropegateNetwork import newPropegateNetwork
    # newPropegateNetwork(json_network["Layers"])


    def result_reader(q):
        # read and print whatever comes onto results queue
        while True:
            while not q.empty():
                res = q.get()
                import pprint
                
                print("RESULTS:" + pprint.pformat(res, depth=2))
            import time
            time.sleep(0.5)
        
    threading.Thread(target=result_reader, args=(rq,)).start()            

    # import pdb; pdb.set_trace()
    mode = 'normal'
    session_history = SessionHistory() 
    #session_history = session_history_lw

    sph = SessionProcessHandler(graph_dict, data_container, cq, rq, mode)    
    core = Core(CodeHq, graph_dict, data_container, session_history, sph, mode=mode)
    core.run()

    

