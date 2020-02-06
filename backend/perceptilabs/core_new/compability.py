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


def policy_classification(graphs, sanitized_to_name, sanitized_to_id):

    def get_layer_inputs_and_outputs(graph, node, trn_node):
        data = {}
        data['Y'] = trn_node.layer.layer_outputs.get(node.layer_id) # OUTPUT: ndarrays of layer-speci
        data['X'] = {} # This layer works with layer names...
        for input_node in graph.get_input_nodes(node):
            input_name = sanitized_to_name[input_node.layer_id]
            input_value = trn_node.layer.layer_outputs.get(input_node.layer_id)
            data['X'][input_name] = {'Y': input_value}
        return data
    
    def get_layer_weights_and_biases(node, trn_node):
        data = {}        
        w = next(iter(trn_node.layer.layer_weights.get(node.layer_id, {}).values()), None) # Get the first set of weights, if any
        if w is not None:
            data['W'] = w

        b = next(iter(trn_node.layer.layer_biases.get(node.layer_id, {}).values()), None)
        if b is not None:
            data['b'] = b
        return data

    def get_layer_gradients(layer_id, graphs):
        data = {}

        min_list, max_list, avg_list = [], [], []
        for graph in graphs:
            gradient_dict = graph.active_training_node.layer.layer_gradients.get(layer_id, {})


            # (1) compute the min, max and average for gradients w.r.t each tensor in a layer
            # (2) compute min, max and average among the output of (1)
            # is there a more meaningful way to do it?
            
            layer_min_list, layer_max_list, layer_avg_list = [], [], []
            for name, grad in gradient_dict.items():
                grad = np.asarray(grad)
            
                layer_min_list.append(np.min(grad))
                layer_max_list.append(np.max(grad))
                layer_avg_list.append(np.average(grad))

            if len(gradient_dict) > 0:
                min_list.append(np.min(layer_min_list))
                max_list.append(np.max(layer_max_list))
                avg_list.append(np.average(layer_avg_list))

        data['Gradient'] = {
            'Min': min_list,
            'Max': max_list,
            'Average': avg_list
        }
        return data

    def get_metrics(graphs):
        data = {}
        x = np.random.random((60,)) # TODO: these are temporary whiel figuring out F1 and AUC
        y = np.random.random((10,))


        # ---- Get the metrics for ongoing epoch
        current_epoch = graphs[-1].active_training_node.layer.epoch

        acc_trn_iter = []
        loss_trn_iter = []
        f1_trn_iter = x
        auc_trn_iter = x
        
        acc_val_iter = []
        loss_val_iter = []
        f1_val_iter = x
        auc_val_iter = x
        
        for graph in graphs:
            trn_layer = graph.active_training_node.layer
            if trn_layer.epoch == current_epoch and trn_layer.status == 'training':
                acc_trn_iter.append(trn_layer.accuracy_training)
                loss_trn_iter.append(trn_layer.loss_training)                
                #f1_trn_iter.append(trn_layer.f1_score_training) # TODO: fix these two
                #auc_trn_iter.append(trn_layer.auc_training)                

            if trn_layer.epoch == current_epoch and trn_layer.status == 'validation':
                acc_val_iter.append(trn_layer.accuracy_validation)
                loss_val_iter.append(trn_layer.loss_validation)                
                #f1_val_iter.append(trn_layer.f1_score_validation) # TODO: fix these two
                #auc_val_iter.append(trn_layer.auc_validation)                

        # ---- Get the metrics from the end of each epoch
        acc_trn_epoch = []
        loss_trn_epoch = []
        f1_trn_epoch = x
        auc_trn_epoch = x
        
        acc_val_epoch = []
        loss_val_epoch = []
        f1_val_epoch = x
        auc_val_epoch = x

        idx = 1
        while idx < len(graphs):
            is_new_epoch = graphs[idx].active_training_node.layer.epoch != graphs[idx-1].active_training_node.layer.epoch
            #is_final_iteration = idx == len(graphs) - 1
            is_final_iteration = False

            if is_new_epoch or is_final_iteration:
                trn_layer = graphs[idx-1].active_training_node.layer                                                
                acc_trn_epoch.append(trn_layer.accuracy_training)
                loss_trn_epoch.append(trn_layer.loss_training)
                # TODO: f1 and auc train
                
                acc_val_epoch.append(trn_layer.accuracy_validation)
                loss_val_epoch.append(trn_layer.loss_validation)
                # TODO: f1 and auc val
            idx += 1

        # ---- Update the dicts
        data['acc_train_iter'] = acc_trn_iter
        data['loss_train_iter'] = loss_trn_iter
        data['f1_train_iter'] = f1_trn_iter
        data['auc_train_iter'] = auc_trn_iter
        
        data['acc_val_iter'] = acc_val_iter
        data['loss_val_iter'] = loss_val_iter
        data['f1_val_iter'] = f1_val_iter
        data['auc_val_iter'] = auc_val_iter        
                
        data['acc_training_epoch'] = acc_trn_epoch
        data['loss_training_epoch'] = loss_trn_epoch
        data['f1_training_epoch'] = f1_trn_epoch
        data['auc_training_epoch'] = auc_trn_epoch
        
        data['acc_validation_epoch'] = acc_val_epoch
        data['loss_validation_epoch'] = loss_val_epoch
        data['f1_validation_epoch'] = f1_val_epoch
        data['auc_validation_epoch'] = auc_val_epoch        

        return data

    current_graph = graphs[-1]
    
    trn_node = current_graph.active_training_node
    if trn_node.layer.status != 'testing':
        train_dict = {}        

        # ----- Get layer specific data.
        for node in current_graph.nodes:
            data = {}
            true_id = sanitized_to_id[node.layer_id] # nodes use spec names for layer ids

            if node.layer.variables is not None:
                data.update(node.layer.variables)
            data.update(get_layer_inputs_and_outputs(current_graph, node, trn_node))
            data.update(get_layer_weights_and_biases(node, trn_node))
            data.update(get_layer_gradients(node.layer_id, graphs))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(graphs))
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
    elif trn_node.layer.status == 'testing':
        test_dict = {}
        for node in current_graph.nodes:
            data = {}
            true_id = sanitized_to_id[node.layer_id] # nodes use spec names for layer ids
            data.update(get_layer_inputs_and_outputs(current_graph, node, trn_node))
            test_dict[true_id] = data
        
        training_status = 'Finished'
        status='Running'
        test_status='Waiting'

        max_itr_tst = 0
        if trn_node.layer.size_testing and trn_node.layer.batch_size:
            max_itr_tst = np.ceil(trn_node.layer.size_training/trn_node.layer.batch_size)

        true_id = sanitized_to_id[trn_node.layer_id]            
        test_dict[true_id]['acc_training_epoch'] = 0
        test_dict[true_id]['f1_training_epoch'] = 0
        test_dict[true_id]['auc_training_epoch'] = 0
                
        test_dict[true_id]['acc_validation_epoch'] = 0
        test_dict[true_id]['f1_validation_epoch'] = 0
        test_dict[true_id]['auc_validation_epoch'] = 0

        test_dict[true_id]['acc_train_iter'] = 0
        test_dict[true_id]['f1_train_iter'] = 0
        test_dict[true_id]['auc_train_iter'] = 0
                
        test_dict[true_id]['acc_val_iter'] = 0
        test_dict[true_id]['f1_val_iter'] = 0
        test_dict[true_id]['auc_val_iter'] = 0

        result_dict = {
            "maxTestIter": max_itr_tst,
            "testDict": test_dict,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }
        return result_dict


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
        
        #import uuid
        #session_id = uuid.uuid4().hex        
        #core.deploy(self._graph_spec, session_id)

        while core.is_running:
            time.sleep(0.5)

            while not self._command_queue.empty():
                command = self._command_queue.get()
                self._send_command(core, command)

            #core.step()
                
            results = self._get_results_dict(core.graphs)
            self._result_queue.put(results)

    def _send_command(self, core, command):
        pass
    
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
        if graph is None:
            log.debug("graph is None, returning empty results")
            return {}

        # TODO: if isinstance(training_layer, Classification) etc
        
        result_dict = policy_classification(graph, self._sanitized_to_name, self._sanitized_to_id)
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
    from perceptilabs.core_new.deployment import InProcessDeploymentPipe
    from perceptilabs.script.factory import ScriptFactory
    from perceptilabs.core_new.layers.replication import BASE_TO_REPLICA_MAP    

    with open('net.json_', 'r') as f:
        network = json.load(f)

        for _id, layer in network['Layers'].items():
            if layer['Type'] == 'TrainNormal':
                layer['Properties']['Distributed'] = False
        

    script_factory = ScriptFactory()
    deployment_pipe = InProcessDeploymentPipe(script_factory)
    
    replica_by_name = {repl_cls.__name__: repl_cls for repl_cls in BASE_TO_REPLICA_MAP.values()}    
    graph_builder = GraphBuilder(replica_by_name)                

    commandQ=queue.Queue()
    resultQ=queue.Queue()
    
    core = CompabilityCore(commandQ, resultQ, graph_builder, deployment_pipe, network)
    core.run()
        
