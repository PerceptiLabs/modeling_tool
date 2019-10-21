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
from core_new.history import SessionHistory
from core_new.session import LayerSession, LayerSessionStop, LayerIo
from core_new.data.policies import TrainValDataPolicy, TestDataPolicy, TrainReinforceDataPolicy

log = logging.getLogger(__name__)


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
            ## add headless commands
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
        outShape = ''
        # Y = session.outputs.locals.get('Y')
        # if isinstance(Y, tf.Tensor):
        #     outShape = Y.shape.as_list()
        #     outShape=outShape[1:]
        #     if not outShape:
        #         outShape=[1]
                
        sample = ''
        inShape=''
        default_var=''
        layer_keys=[]
        if session.layer_id in data_container:
            layer_dict = data_container[session.layer_id]

            if 'Y' in layer_dict:
                Y = layer_dict['Y'] 
                if isinstance(Y, tf.Tensor):
                    outShape = Y.shape.as_list()
                    outShape=outShape[1:]
                else:
                    outShape = np.shape(Y)[1:]
                if not outShape:
                    outShape=[1]
            
            if 'sample' in layer_dict:
                sample = layer_dict['sample']
                default_var = 'sample'
            elif 'Y' in layer_dict:
                sample = layer_dict['Y']
                default_var = 'Y'

            if "X" in layer_dict and "Y" in layer_dict["X"]:
                Xy = layer_dict["X"]["Y"]
                if isinstance(Xy, tf.Tensor):
                    inShape = Xy.shape.as_list()
                    inShape=inShape[1:]
                    if not inShape:
                        inShape=[1]

            layer_keys = list(layer_dict.keys())

            sample=self._evalSample(sample)

        self._put_in_dict(session.layer_id,{'Sample': sample, 'outShape': outShape, 'inShape': str(inShape).replace("'",""), 'Variables': layer_keys, 'Default_var':default_var})
        # print("Session dict:", self.to_dict())

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
    def __init__(self, codehq, graph_dict, data_container, session_history, module_provider, session_process_handler=None,
                 layer_extras_reader=None, skip_layers=None, tf_eager=False, checkpoints=None): 
        self._graph = graph_dict
        self._codehq = codehq
        self._data_container = data_container
        self._tf_eager = tf_eager
        self._session_process_handler = session_process_handler
        self._layer_extras_reader = layer_extras_reader
        self._session_history = session_history        
        self._skip_layers = skip_layers if skip_layers is not None else []
        self._module_provider = module_provider
        self._checkpoints = checkpoints

    def run(self):
        log.info("Running core [{}]".format(self.__class__.__name__))
        self._data_container.reset()
        self._session_history.cache.invalidate(keep_layers=self._graph.keys())

        log.info("Layers will be executed in the following order: " \
                 + ", ".join([id_ + ' [' + cont["Info"]["Type"]+']' for id_, cont in self._graph.items()]))

        
        if len(self._module_provider.hooks) > 0:
            targets = [x for x in self._module_provider.hooks.keys()]
            log.info("Module hooks installed are: {}".format(", ".join(targets)))
        else:
            log.info("No module hooks installed")        

        if self._tf_eager:
            set_tensorflow_mode('eager')
        else:
            set_tensorflow_mode('graph') # Default to graph mode

        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]
            if not (content["Info"]["Properties"] or ("Code" in content["Info"] and content["Info"]["Code"])):
                continue
            if layer_type in self._skip_layers:
                log.info("Layer {} [{}] in skip list. Skipping.".format(layer_id, layer_type))
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
        code_gen = self._codehq.get_code_generator(id_, content)
        log.debug(repr(code_gen))
        
        globals_, locals_ = self._get_globals_and_locals(input_layer_ids=content['Con'])  

        if 'checkpoint' in content['Info'] and content['Info']['checkpoint'] and type(code_gen).__name__ == "CustomCodeGenerator":
            import pdb; pdb.set_trace()
            locals_.update({"checkpoint":self._checkpoints[content['Info']['checkpoint'][1]]})
            code_gen.replace_ckpt_references()

        code = code_gen.get_code()

        session = LayerSession(id_, content['Info']['Type'], code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler,
                               cache=self._session_history.cache)   

        try:        
            session.run()
        except LayerSessionStop:
            raise # Not an error. Re-raise.
        except SyntaxError as e:
            self.on_error(session, traceback.format_exc())            
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.read_syntax_error(session)
            else:
                raise
        except Exception as e:
            self.on_error(session, traceback.format_exc())
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.read_error(session,e)
            else:
                raise


        self._session_history[id_] = session

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.read(session, self._data_container)
            
        log.debug("Done running layer {}".format(id_))#. Locals:  {}".format(id_, session.outputs.locals))
                  
    def _get_globals_and_locals(self, input_layer_ids):
        outputs = self._session_history.merge_session_outputs(input_layer_ids)

        # Load globals.
        # Note that modules imported via module provider will overwrite in-code imports        
        # globals_ = {"tf": tf, "np": np, "pd":pd, "gym":gym}
        globals_ = {}
        globals_.update(outputs.globals) # Other global variables
        globals_.update(self._module_provider.modules) # Default modules. 

        if log.isEnabledFor(logging.DEBUG): # TODO: remove this when done
            from code_generator.tensorflow import DummyEnv
            globals_['DummyEnv'] = DummyEnv
        
        locals_=outputs.locals

        return globals_, locals_        

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
                 module_provider, session_process_handler):
        super().__init__(codehq, graph_dict, data_container,
                         session_history, module_provider,
                         session_process_handler=session_process_handler)

        
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


    from core_new.lightweight import LightweightCore, placeholder_hook_1
    
    module_provider = ModuleProvider()
    module_provider.load('tensorflow', as_name='tf')
    module_provider.load('numpy', as_name='np')

    module_provider.install_hook('tf.placeholder', placeholder_hook_1, include_vars=True)


    graph_dict = graph.graphs
    data_container = DataContainer()
    
    session_history = SessionHistory()
    extras_reader = LayerExtrasReader()

    lw_core = LightweightCore(CodeHq, graph_dict, data_container, 
                              session_history, module_provider, extras_reader)    
    lw_core.run()
    print(extras_reader.to_dict())

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
    mode = 'normal'
    # session_history = SessionHistory() 
    # #session_history = session_history_lw


   
    module_provider = ModuleProvider()
    module_provider.load('tensorflow', as_name='tf')
    module_provider.load('numpy', as_name='np')
   

    sph = SessionProcessHandler(graph_dict, data_container, cq, rq)    
    core = Core(CodeHq, graph_dict, data_container, session_history, module_provider, sph)
    import threading
    threading.Thread(target=core.run).start()
    # core.run()
    import time
    time.sleep(2)
    cq.put("pause")
    time.sleep(2)
    cq.put("unpause")
    time.sleep(2)
    cq.put("pause")
