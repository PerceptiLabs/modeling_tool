import copy
import time
import pprint
import logging



from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *
from perceptilabs.core_new.layers.replicas import NotReplicatedError

log = logging.getLogger(__name__)


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
        try:
            return self._get_results_dict_internal(graph)
        except:
            log.exception('Error when getting results dict')
            return {}
                
    
    def _get_results_dict_internal(self, graph):
        if graph is None:
            log.debug("graph is None, returning empty results")
            return {}

        self._print_debug_info(graph)

        training_layer = graph.active_training_node.layer
        import numpy as np

        itr = 0
        max_itr = 0
        epoch = 0
        max_epoch = -1
        batch_size = training_layer.batch_size
        itr_trn = 0

        train_dict = {}
        for node in graph.nodes:
            layer = node.layer
            layer_id = node.layer_id
            true_id = self._sanitized_to_id[layer_id] # nodes use spec names for layer ids
            data = {}

            data['Y'] = training_layer.layer_outputs.get(layer_id) # OUTPUT: ndarrays of layer-specific dims
            w = next(iter(training_layer.layer_weights.get(layer_id, {}).values()), None)
            if w is not None:
                data['W'] = w

            b = next(iter(training_layer.layer_biases.get(layer_id, {}).values()), None)                            
            if b is not None:
                data['b'] = b
            
            gradient_dict = training_layer.layer_gradients.get(layer_id, {})
            
            for name, grad in gradient_dict.items():
                grad = np.asarray(grad)
                axis = tuple(range(1, grad.ndim))
                data['Gradient'] = {
                    'Min': np.min(grad, axis=axis).tolist(),
                    'Max': np.max(grad, axis=axis).tolist(),
                    'Average': np.average(grad, axis=axis).tolist()
                }
                
            data['X'] = {} # This layer works with layer names...
            for input_node in graph.get_input_nodes(node):
                input_name = self._sanitized_to_name[input_node.layer_id]
                input_value = training_layer.layer_outputs.get(input_node.layer_id)
                data['X'][input_name] = {'Y': input_value}
                                
            if isinstance(layer, Tf1xClassificationLayer):
                x = np.random.random((60,))
                y = np.random.random((10,))
                
                if len(layer.accuracy_training) > 0 and len(layer.loss_training) > 0:
                    data['acc_train_iter'] = np.array(layer.accuracy_training[-1])
                    data['loss_train_iter'] = np.array(layer.loss_training[-1])
                    data['f1_train_iter'] = x
                    data['auc_train_iter'] = x

                if len(layer.accuracy_training) > 1 and len(layer.loss_training) > 1:                    
                    data['acc_training_epoch'] = np.array([epoch_list[-1] for epoch_list in layer.accuracy_training])
                    data['loss_training_epoch'] = np.array([epoch_list[-1] for epoch_list in layer.loss_training])
                    data['f1_training_epoch'] = y
                    data['auc_training_epoch'] = y

                if len(layer.accuracy_validation) > 0 and len(layer.loss_validation) > 0:                    
                    
                    data['acc_val_iter'] = np.array(layer.accuracy_validation[-1])
                    data['loss_val_iter'] = np.array(layer.loss_training[-1])
                    data['f1_val_iter'] = x
                    data['auc_val_iter'] = x
                    
                if len(layer.accuracy_validation) > 1 and len(layer.loss_validation) > 1:                                        
                    data['acc_validation_epoch'] = np.array([epoch_list[-1] for epoch_list in layer.accuracy_validation])
                    data['loss_validation_epoch'] = np.array([epoch_list[-1] for epoch_list in layer.loss_validation])
                    data['f1_validation_epoch'] = y
                    data['auc_validation_epoch'] = y



                    
            elif isinstance(layer, DataLayer): # using elif since training layers are also datalayers. this need to be generalized.
                # TODO: get_active_data_node() instead?
                max_itr_trn = -1
                max_itr_val = -1
                max_itr = -1

                if layer.size_training and layer.size_validation and batch_size:
                    max_itr_trn = np.ceil(layer.size_training/batch_size)
                    max_itr_val = np.ceil(layer.size_validation/batch_size)
                    max_itr = max_itr_trn + max_itr_val

            train_dict[true_id] = data

        if training_layer.is_paused:
            status = 'Paused'
        else:
            status = 'Running'

        training_status = 'Waiting'
        if training_layer.status == 'created':
            training_status = 'Waiting'
        elif training_layer.status in ['initializing', 'training']:
            training_status = 'Training'
        elif training_layer.status == 'validation':
            training_status = 'Validation'
        elif training_layer.status == 'finished':
            training_status = 'Finished'

        if training_layer.training_iteration is not None and training_layer.validation_iteration is not None:
            itr = training_layer.training_iteration + training_layer.validation_iteration
        else:
            itr = 0

        result_dict = {
            "iter": itr,
            "maxIter": max_itr,
            "epoch": epoch,
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            "trainingIterations": training_layer.training_iteration,
            "trainDict": train_dict,
            "trainingStatus": training_status,  
            "status": status,
            "progress": training_layer.progress
        }
        return result_dict

    def _print_debug_info(self, graph):
        if not log.isEnabledFor(logging.DEBUG):
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
        
