import copy
import time
import pprint
import logging
import numpy as np


from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import NotReplicatedError

log = logging.getLogger(__name__)


def policy_classification(graph, sanitized_to_name, sanitized_to_id):

    def get_layer_inputs_and_outputs(node, trn_node):
        data = {}
        data['Y'] = trn_node.layer.layer_outputs.get(node.layer_id) # OUTPUT: ndarrays of layer-speci
        data['X'] = {} # This layer works with layer names...
        for input_node in graph.get_input_nodes(node):
            input_name = sanitized_to_name[input_node.layer_id]
            input_value = trn_node.layer.layer_outputs.get(input_node.layer_id)
            data['X'][input_name] = {'Y': input_value}
            
        #if node == trn_node:
        #    import pdb;pdb.set_trace()
            
        return data
    
    def get_layer_weights_and_biases(node, trn_node):
        data = {}        
        w = next(iter(trn_node.layer.layer_weights.get(node.layer_id, {}).values()), None)
        if w is not None:
            data['W'] = w

        b = next(iter(trn_node.layer.layer_biases.get(node.layer_id, {}).values()), None)
        if b is not None:
            data['b'] = b
        return data

    def get_layer_gradients(node, trn_node):
        data = {}
        gradient_dict = trn_node.layer.layer_gradients.get(node.layer_id, {})
        
        for name, grad in gradient_dict.items():
            grad = np.asarray(grad)
            axis = tuple(range(1, grad.ndim))
            data['Gradient'] = {
                'Min': np.min(grad, axis=axis).tolist(),
                'Max': np.max(grad, axis=axis).tolist(),
                'Average': np.average(grad, axis=axis).tolist()
            }
        return data

    def get_metrics(trn_node):
        data = {}
        x = np.random.random((60,)) # TODO: these are temporary whiel figuring out F1 and AUC
        y = np.random.random((10,))
        
        if len(trn_node.layer.accuracy_training) > 0 and len(trn_node.layer.loss_training) > 0:
            data['acc_train_iter'] = np.array(trn_node.layer.accuracy_training[-1])
            data['loss_train_iter'] = np.array(trn_node.layer.loss_training[-1])
            data['f1_train_iter'] = x
            data['auc_train_iter'] = x

        if len(trn_node.layer.accuracy_training) > 1 and len(trn_node.layer.loss_training) > 1:                    
            data['acc_training_epoch'] = np.array([epoch_list[-1] for epoch_list in trn_node.layer.accuracy_training])
            data['loss_training_epoch'] = np.array([epoch_list[-1] for epoch_list in trn_node.layer.loss_training])
            data['f1_training_epoch'] = y
            data['auc_training_epoch'] = y

        if len(trn_node.layer.accuracy_validation) > 0 and len(trn_node.layer.loss_validation) > 0:                    
                    
            data['acc_val_iter'] = np.array(trn_node.layer.accuracy_validation[-1])
            data['loss_val_iter'] = np.array(trn_node.layer.loss_training[-1])
            data['f1_val_iter'] = x
            data['auc_val_iter'] = x
                    
        if len(trn_node.layer.accuracy_validation) > 1 and len(trn_node.layer.loss_validation) > 1:                                        
            data['acc_validation_epoch'] = np.array([epoch_list[-1] for epoch_list in trn_node.layer.accuracy_validation])
            data['loss_validation_epoch'] = np.array([epoch_list[-1] for epoch_list in trn_node.layer.loss_validation])
            data['f1_validation_epoch'] = y
            data['auc_validation_epoch'] = y
        return data

    trn_node = graph.active_training_node
    if trn_node.layer.status != 'testing':
        train_dict = {}        

        # ----- Get layer specific data.
        for node in graph.nodes:
            data = {}
            true_id = sanitized_to_id[node.layer_id] # nodes use spec names for layer ids            
            data.update(get_layer_inputs_and_outputs(node, trn_node))
            data.update(get_layer_weights_and_biases(node, trn_node))
            data.update(get_layer_gradients(node, trn_node))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(trn_node))
        train_dict[true_trn_id].update(data)

        itr = 0
        max_itr = 0
        epoch = 0
        max_epoch = -1
        itr_trn = 0
        max_itr_trn = -1
        max_itr_val = -1
        max_itr = -1

        batch_size = trn_node.layer.batch_size
        if trn_node.layer.size_training and trn_node.layer.size_validation and batch_size:
            max_itr_trn = np.ceil(trn_node.layer.size_training/batch_size)
            max_itr_val = np.ceil(trn_node.layer.size_validation/batch_size)
            max_itr = max_itr_trn + max_itr_val

        if trn_node.layer.training_iteration is not None and trn_node.layer.validation_iteration is not None:
            itr = trn_node.layer.training_iteration + trn_node.layer.validation_iteration
        else:
            itr = 0
                    
        training_status = 'Waiting'
        if trn_node.layer.status == 'created':
            training_status = 'Waiting'
        elif trn_node.layer.status in ['initializing', 'training']:
            training_status = 'Training'
        elif trn_node.layer.status == 'validation':
            training_status = 'Validation'
        elif trn_node.layer.status == 'finished':
            training_status = 'Finished'

        if trn_node.layer.is_paused:
            status = 'Paused'
        else:
            status = 'Running'

        result_dict = {
            "iter": itr,
            "maxIter": max_itr,
            "epoch": epoch,
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            "trainingIterations": trn_node.layer.training_iteration,
            "trainDict": train_dict,
            "trainingStatus": training_status,  
            "status": status,
            "progress": trn_node.layer.progress
        }
        return result_dict
        
    else:
        return {}


class CompabilityCore:
    def __init__(self, command_queue, result_queue, graph_builder, deployment_pipe, graph_spec):
        self._command_queue = command_queue
        self._result_queue = result_queue
        self._graph_builder = graph_builder
        self._deployment_pipe = deployment_pipe
        self._graph_spec = copy.deepcopy(graph_spec)

        self._sanitized_to_id = {sanitize_layer_name(spec['Name']): id_ for id_, spec in graph_spec['Layers'].items()}
        self._sanitized_to_name = {sanitize_layer_name(spec['Name']): spec['Name'] for spec in graph_spec['Layers'].values()}        

    def run(self):
        set_tensorflow_mode('graph')
        core = Core(self._graph_builder, self._deployment_pipe)
        core.run(self._graph_spec)

        while core.is_running:
            time.sleep(0.5)

            while not self._command_queue.empty():
                command = self._command_queue.get()
                self._send_command(core, command)
                
            results = self._get_results_dict(core.graph)
            self._result_queue.put(results)

    def _send_command(self, core, command):
        pass
    
    def _get_results_dict(self, graph):
        self._print_graph_debug_info(graph)
        
        result_dict = {}        
        try:
            result_dict = self._get_results_dict_internal(graph)
        except:
            log.exception('Error when getting results dict')
        finally:
            self._print_result_dict_debug_info(result_dict)
            return result_dict                
    
    def _get_results_dict_internal(self, graph):
        if graph is None:
            log.debug("graph is None, returning empty results")
            return {}

        # TODO: if isinstance(training_layer, Classification) etc
        
        result_dict = policy_classification(graph, self._sanitized_to_name, self._sanitized_to_id)
        return result_dict

    def _print_graph_debug_info(self, graph):
        if not log.isEnabledFor(logging.DEBUG):
            return

        if graph is None:
            log.debug("Graph is None")
            return

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
        if not log.isEnabledFor(logging.DEBUG):
            return

        from perceptilabs.utils import stringify
        text = stringify(result_dict, indent=4)
        log.debug("result_dict: \n" + text)
        


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
                        level=logging.DEBUG)


    
    import json
    import queue
    from perceptilabs.core_new.compability import CompabilityCore
    from perceptilabs.core_new.graph.builder import ReplicatedGraphBuilder
    from perceptilabs.core_new.deployment import InProcessDeploymentPipe
    from perceptilabs.script.factory import ScriptFactory

    with open('net.json_', 'r') as f:
        network = json.load(f)

        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = False
        

    script_factory = ScriptFactory()
    deployment_pipe = InProcessDeploymentPipe(script_factory)
    graph_builder = ReplicatedGraphBuilder(client=None)                

    commandQ=queue.Queue()
    resultQ=queue.Queue()
    
    core = CompabilityCore(commandQ, resultQ, graph_builder, deployment_pipe, network)
    core.run()
        
