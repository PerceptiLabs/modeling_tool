import logging
import re
import sys
import copy
import time
import pprint
import logging
import numpy as np
import traceback
import tensorflow as tf
import pandas as pd
from collections import namedtuple
# import gym

from perceptilabs.graph import Graph
from perceptilabs.modules import ModuleProvider
from perceptilabs.core_new.data import DataContainer
from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.extras import LayerExtrasReader
from perceptilabs.core_new.errors import LayerSessionAbort
from perceptilabs.core_new.history import SessionHistory, HistoryInputException
from perceptilabs.core_new.session import LayerSession, LayerSessionStop, LayerIo
from perceptilabs.core_new.data.policies import TrainValDataPolicy, TestDataPolicy, TrainReinforceDataPolicy
from perceptilabs.utils import stringify, line_nums
from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER



logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)


def v2_insert_checkpoint_values(layer_id, layer_name, layer_type, code, values):
    """ Function used to restore core_v2 checkpoints 

    This function will fail miserably if values-to-be-restored are named differently in v1 and v2."""
    values = values.copy()
    
    # Since checkpoints generated in v2 might be saved with a different TF api, we need to add aliases
    pattern = rf'{layer_type}_{layer_name}\.S([a-zA-Z1-9]*):0\/\.ATTRIBUTES\/VARIABLE_VALUE'
    for old_name, value in values.items():
        match = re.search(pattern, old_name)
        if match:
            values[match.group(1)] = old_name

    lines = code.split('\n')
    new_code = ''

    restored_vars = set()
    ignored_vars = set()
    n_matches = 0
    
    pattern = r'([a-zA-Z1-9]*) = tf.Variable\((.*)\)'
    def repl_fn(match):
        nonlocal n_matches
        n_matches += 1
        assign_var = match.group(1)
        initial_var = match.group(2).split(',')[0]

        if assign_var in values:
            ckpt_name = values[assign_var]
            new_str  = f'{initial_var} = checkpoint["{ckpt_name}"]\n'
            new_str += f'{assign_var} = tf.Variable({match.group(2)})\n'
            restored_vars.add(assign_var)                
            return new_str
        else:
            ignored_vars.add(assign_var)
            return match.string        

    new_code = re.sub(pattern, repl_fn, code)

    logger.info(f'Inserted {len(restored_vars)} checkpoint values into layer {layer_id} [{layer_type}].')
    if len(ignored_vars) > 0 and n_matches > 0:
        logger.warning(f'Ignored {len(ignored_vars)} TensorFlow variable creations!')
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"Restored checkpoint values = {', '.join(restored_vars)}, ignored = {', '.join(ignored_vars)}\n"
            f"Original code: \n{line_nums(code)}\n"
            f"New code: \n{line_nums(new_code)}\n"
        )
        
    return new_code


def make_graph_spec_conform_to_schema(graph_spec):
    #graph_spec = graph_spec['Layers'] # REMOVE    

    edges = []
    nodes = []
    for from_id, layer_spec in graph_spec.items():
        # Nodes. For now, we don't include any detailed parameters...
        layer_spec = layer_spec['Info']
        
        from perceptilabs.core_new.layers.definitions import DEFINITION_TABLE        
        def_ = DEFINITION_TABLE.get(layer_spec['Type'])        
        node = {
            'type': def_.template_macro,
            'id': from_id,
        }
        nodes.append(node)
        
        # Edges
        fwd_cons = [layer_id for layer_id, _ in layer_spec['forward_connections']]
        for to_id in fwd_cons:
            edges.append([from_id, to_id])

    return {
        'nodes': nodes,
        'edges': edges
    }


def collect_start_data(graph_dict, data_container, training_sess_id):
    """ quick fix for creating 'training_started' event """

    if not all(layer_id in data_container for layer_id in graph_dict.keys()):
        # We'll use this to signify that the training has actually started
        return False    
    
    import functools
    import operator

    formatted_graph = make_graph_spec_conform_to_schema(graph_dict)
    
    n_params = 0
    for layer_id in graph_dict.keys():
        layer_dict = data_container[layer_id]

        if 'W' in layer_dict:
            n_params += functools.reduce(operator.mul, layer_dict['W'].shape.as_list())
        if 'b' in layer_dict:
            n_params += functools.reduce(operator.mul, layer_dict['b'].shape.as_list())

    data_logger.info(
        "training_started",
        training_session_id = training_sess_id,        
        graph_spec=formatted_graph,
        n_parameters=n_params
    )    
    return True


import time
import psutil


class Reservoir:
    def __init__(self, max_items=10):
        self._data = []
        self._max_items = max_items
        self._counter = 0
        
    def try_sample(self, x):
        if len(self._data) < self._max_items:
            self._data.append(x)
        else:
            idx = np.random.randint(0, self._counter + 1)
            if idx < self._max_items: # Replace
                self._data[idx] = x        
        self._counter += 1

    def __repr__(self):
        return repr(self._data)

    @property
    def data(self):
        return self._data.copy()
        

class EndedDataCollector:
    def __init__(self, training_sess_id):
        self._training_sess_id = training_sess_id
        self._t_on_process = []
        self._memory_on_process = []

        self._data_outputs = {}
        self._data_shapes = {}
        self._data_columns = {}        
        self._data_sizes = {}
        self._data_paths = {}
        
    def on_process(self, graph_dict, data_container, results_dict):
        self._graph_dict = graph_dict
        self._data_container = data_container
        self._t_on_process.append(time.time())
        self._memory_on_process.append((psutil.virtual_memory(), psutil.swap_memory()))

        for layer_id in graph_dict.keys():
            if graph_dict[layer_id]['Info']['Type'] == 'DataData':

                if not 'trainDict' in results_dict:
                    continue

                layer_results = results_dict['trainDict'][layer_id].copy()

                y = layer_results['Y'][0]
                if layer_id not in self._data_shapes:
                    self._data_shapes[layer_id] = y.shape

                if y.ndim > 0:
                    y = y.reshape(y.shape[0], -1).squeeze() # Flatten if necessary.
                    
                if layer_id not in self._data_outputs:
                    self._data_outputs[layer_id] = Reservoir(max_items=100)
                self._data_outputs[layer_id].try_sample(y)                    
                
                if layer_id not in self._data_sizes:
                    self._data_sizes[layer_id] = {
                        'trn_size': data_container[layer_id].get('trn_sz_tot', -1),
                        'val_size': data_container[layer_id].get('val_sz_tot', -1),
                        'tst_size': data_container[layer_id].get('tst_sz_tot', -1)
                    }

                if layer_id not in self._data_paths:
                    self._data_paths[layer_id] = []
                    for s in graph_dict[layer_id]['Info']['Properties']['accessProperties']['Sources']:
                        self._data_paths[layer_id].append(s['path'])

                if layer_id not in self._data_columns:
                    self._data_columns[layer_id] = data_container[layer_id].get('cols', []).copy()                    
    def start(self):
        self._t_start = time.time()
    
    def finish(self):
        if len(self._t_on_process) == 0:
            return

        import functools
        import operator
        
        n_params = 0
        for layer_id in self._graph_dict.keys():
            layer_dict = self._data_container[layer_id]
            
            if 'W' in layer_dict:
                n_params += functools.reduce(operator.mul, layer_dict['W'].shape.as_list())
            if 'b' in layer_dict:
                n_params += functools.reduce(operator.mul, layer_dict['b'].shape.as_list())
        

        formatted_graph = make_graph_spec_conform_to_schema(self._graph_dict)        
        import numpy as np
        t_stop = time.time()
        t_duration = t_stop - self._t_start
        t_processing = np.subtract(self._t_on_process + [t_stop], [self._t_start] + self._t_on_process).tolist()
        data_meta_list = []
        for layer_id in self._data_outputs.keys():
            y_samples = np.array(self._data_outputs[layer_id].data)

            #axis = tuple(range(1, y_samples.ndim)) # compute metrics for each sample in this "batch"

            data_meta = {
                'layer_id': layer_id,
                'training_set_size': self._data_sizes[layer_id].get('trn_size', -1),
                'validation_set_size': self._data_sizes[layer_id].get('val_size', -1),
                'testing_set_size': self._data_sizes[layer_id].get('tst_size', -1),
                'example_mean': y_samples.mean(),
                'example_max': y_samples.max().tolist(),
                'example_min': y_samples.min().tolist(),
                'example_std': y_samples.std().tolist(),
                'example_shape': list(self._data_shapes[layer_id])
            }
            data_meta_list.append(data_meta)

        memory_on_process = self._memory_on_process[::20]
        t_processing = t_processing[::20]
        data_logger.info(
            "training_ended",
            training_session_id = self._training_sess_id,                    
            time_total=t_duration,
            time_processing=t_processing,
            memory={
                'physical_total': memory_on_process[0][0].total,
                'physical_available': [x[0].available for x in memory_on_process],
                'swap_total': memory_on_process[0][1].total,
                'swap_free': [x[1].free for x in memory_on_process]
            },
            data_meta=data_meta_list,
            graph_spec=formatted_graph,
            n_parameters=n_params            
        )


class SessionProcessHandler:
    def __init__(self, graph_dict, data_container, command_queue, result_queue, training_sess_id):  # mode
        self._graph = graph_dict
        self._data_container = data_container
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._on_process_counter = 0

        self._training_sess_id = training_sess_id
        self._has_collected_start_data = False

        self._ended_data_collector = EndedDataCollector(training_sess_id)

    def on_start(self):
        self._ended_data_collector.start()
    
    def on_finish(self):
        try:
            self._ended_data_collector.finish()
        except:
            logger.exception("logging 'on_training_ended' event failed!")
        
    def on_process(self, session, dashboard):
        """ Called in response to 'api.ui.render' calls in the layer code """
        self._handle_commands(session)
        self._send_results(session, dashboard)

        try:
            if not self._has_collected_start_data:
                self._has_collected_start_data = collect_start_data(self._graph, self._data_container, self._training_sess_id)
        except:
            logger.exception("logging 'on_training_started' event failed!")

            
    def _send_results(self, session, dashboard):
        data_policy = self._get_data_policy(session, dashboard)
        results_dict = data_policy.get_results()

        self._ended_data_collector.on_process(self._graph, self._data_container, results_dict)            
        
        self._result_queue.put(results_dict)
        # self._data_container.reset()
        
        #logger.debug("Pushed results onto queue: " + pprint.pformat(results_dict, depth=4))
        #if logger.isEnabledFor(logging.DEBUG): # TODO: remove this when done
            #remapped_dict = boltons.iterutils.remap(results_dict, lambda p, k, v: str(type(v)))
            #logger.debug("Pushed results onto queue: " + pprint.pformat(remapped_dict, depth=10))
        
    def _handle_commands(self, session):
        while not self._command_queue.empty():
            command = self._command_queue.get()
            logger.info("Received command '{}'".format(command))
            
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
                logger.warning("Unknown command: '{}'".format(command))        

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
    def __init__(self, codehq, graph_dict, data_container, session_history, module_provider, error_handler, session_process_handler=None,
                 layer_extras_reader=None, skip_layers=None, tf_eager=False, checkpointValues=None, network_cache=None, core_mode='v1'): 
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
        self._core_mode = core_mode

    def run(self):
        self._reset()        
        self._print_basic_info()
        
        set_tensorflow_mode('eager' if self._tf_eager else 'graph')
        
        for layer_id, content in self._graph.items():
            layer_type = content["Info"]["Type"]

            if self._should_skip_layer(layer_id, content):
                logger.debug("Skipping layer {} [{}]".format(layer_id, layer_type))
                continue

            if self._network_cache is not None:
                if layer_id in self._network_cache and not self._network_cache.needs_update(layer_id, content):
                    logger.info("Using cached layer for layer " +layer_type)
                    self._use_cached_layer(layer_id, self._network_cache[layer_id])
                    continue

            logger.info("Preparing layer session for {} [{}]".format(layer_id, layer_type))
            t_start = time.perf_counter()

            if self._session_process_handler:
                self._session_process_handler.on_start()            
            try:
                self._run_layer(layer_id, content)
            except LayerSessionStop:
                logger.info("Stop requested during session {}".format(layer_id))                
                break
            except LayerSessionAbort:
                logger.info("Error handler aborted session {}".format(layer_id))
                break
            except Exception:
                logger.exception("Exception in %s" % layer_id)
                raise
            finally:
                logger.info("Running layer {} [{}] took {} seconds".format(
                    layer_id, layer_type,
                    time.perf_counter() - t_start
                ))
                if self._session_process_handler:
                    self._session_process_handler.on_finish()                        
                
            

    def _run_layer(self, id_, content):    
        clean_content=copy.deepcopy(content)
        code_gen = self._codehq.get_code_generator(id_, content)
        

        logger.info(repr(code_gen))        
        if logger.isEnabledFor(logging.DEBUG):        
            logger.debug(pprint.pprint(code_gen.get_code()))


        #import pdb; pdb.set_trace()
            
        
        try:
            globals_, locals_ = self._get_globals_and_locals(input_layer_ids=content['Con'])  
        except HistoryInputException:
            if self._layer_extras_reader is not None:
                self._layer_extras_reader.set_empty(id_)
                logger.exception("HistoryInputException for layer %s" % content['Info']['Type'])
                return
            else:
                raise

        if content['Info']['checkpoint'] and type(code_gen).__name__ == "CustomCodeGenerator" and self._checkpointValues and self._core_mode == 'v1':
            locals_.update({"checkpoint":self._checkpointValues[content['Info']['checkpoint'][-1]]})
            code_gen.replace_ckpt_references()
                

        code = code_gen.get_code()
        if content['Info']['checkpoint'] and self._core_mode == 'v2':
            locals_.update({"checkpoint":self._checkpointValues[content['Info']['checkpoint'][-1]]})            
            code = v2_insert_checkpoint_values(id_, content['Info']['Name'], content['Info']['Type'], code, self._checkpointValues[content['Info']['checkpoint'][-1]])            

        if (
                self._core_mode == 'v2' and                
                content['Info'].get('Code') is not None and 
                (content['Info'].get('Code') != '' or (isinstance(content['Info']['Code'], dict) and content['Info']['Code'].get('Output') is not None))
        ):
            warning_message = "Custom code not supported in lightweight core for core mode == 'v2'. Replacing generated code with identity (Y = X['Y'])"
            if logger.isEnabledFor(logging.DEBUG):
                warning_message += "\nOriginal code:\n" + line_nums(code)
            logger.warning(warning_message)

            code = "Y = X['Y']\n"
            
        
        if content['Info']['checkpoint'] and self._core_mode == 'v2':
            locals_.update({"checkpoint":self._checkpointValues[content['Info']['checkpoint'][-1]]})            
            code = v2_insert_checkpoint_values(id_, content['Info']['Name'], content['Info']['Type'], code, self._checkpointValues[content['Info']['checkpoint'][-1]])            

        session = LayerSession(id_, content['Info']['Type'], code,
                               global_vars=globals_,
                               local_vars=locals_,
                               data_container=self._data_container,
                               process_handler=self._session_process_handler,
                               cache=self._session_history.cache)   



        try:
            session.run()
        except LayerSessionStop:
            logger.debug("Raised LayerSessionStop!")
            raise # Not an error. Re-raise.
        except Exception as e:
            logger.exception("Exception when running session: " + str(e) + " will be handled by error handler " + str(self._error_handler))
            self._error_handler.handle_run_error(session, e)
            
        # else:
        #     _save_cache=True

        self._session_history[id_] = session

        if self._layer_extras_reader is not None:
            self._layer_extras_reader.read(session, self._data_container)

        if self._network_cache is not None:
            self._network_cache.update(id_, clean_content, session, self._error_handler[id_] if id_ in self._error_handler.to_dict() else None)
            
        logger.debug("Done running layer {}".format(id_))#. Locals:  {}".format(id_, session.outputs.locals))

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

        # if logger.isEnabledFor(logging.DEBUG): # TODO: remove this when done
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
        logger.info("Running core [{}]".format(self.__class__.__name__))
        
        layer_repr = [id_ + ' [' + cont["Info"]["Type"]+']' for id_, cont in self._graph.items()]
        logger.info("Layers will be executed in the following order: "+ ", ".join(layer_repr))
        
        if len(self._module_provider.hooks) > 0:
            targets = [x for x in self._module_provider.hooks.keys()]
            logger.info("Module hooks installed are: {}".format(", ".join(targets)))
        else:
            logger.info("No module hooks installed")

    def _should_skip_layer(self, layer_id, content):
        layer_type = content["Info"]["Type"]        
        if not (content["Info"]["Properties"] \
                or ("Code" in content["Info"] and content["Info"]["Code"])):
            if self._layer_extras_reader is not None:
                return True
            else:
                raise Exception("Layer {} is empty and can therefore not run.\nMost likely it has not been properly Applied.".format(content["Info"]["Name"]))


        #if content['Info'].get('Code') is not None and self._core_mode == 'v2':
        #    logger.warning(f'Cannot run custom code in core_v2. Skipping layer {layer_id} [{layer_type}]')
        #    return True
            
        # if "Code" in content["Info"] and content["Info"]["Code"]:
        #     logger.info("Layer {} [{}] has custom code. Skipping.".format(layer_id, layer_type))        
           
        #     return True


        if layer_type in self._skip_layers:
            logger.info("Layer {} [{}] in skip list. Skipping.".format(layer_id, layer_type))
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

    with open('net.json_') as f:
        import json
        x = json.load(f)

        make_graph_spec_conform_to_schema(x)
