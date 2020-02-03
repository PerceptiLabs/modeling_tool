import copy
import time
import pprint
import logging



from perceptilabs.core_new.utils import set_tensorflow_mode
from perceptilabs.core_new.graph.utils import sanitize_layer_name
from perceptilabs.core_new.core2 import Core
from perceptilabs.core_new.layers import *

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
        if graph is None:
            log.debug("graph is None, returning empty results")
            return {}

        training_layer = graph.active_training_node.layer

        import numpy as np

        itr = 0
        max_itr = 0
        epoch = 0
        max_epoch = 0
        batch_size = 0
        itr_trn = 0

        log.debug("layer_outputs: " + pprint.pformat(training_layer.layer_outputs))
        train_dict = {}
        
        for node in graph.nodes:
            layer = node.layer
            layer_id = node.layer_id
            true_id = self._sanitized_to_id[layer_id] # nodes use spec names for layer ids
            data = {}

            data['Y'] = training_layer.layer_outputs.get(layer_id) # OUTPUT: ndarrays of layer-specific dims
            data['W'] = np.random.random((10, 28, 28)) # WEIGHTS, ndarray, variable dim 
            data['b'] = np.random.random((10)) # BIAS, ndarray, variable dim
            
            gradient_dict = training_layer.layer_gradients.get(layer_id, {})
            
            for name, grad in gradient_dict.items():
                grad = np.random.random((500, 123)) # TEMPORARY! 
                
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
                data['acc_train_iter'] = x
                data['loss_train_iter'] = x
                data['f1_train_iter'] = x
                data['auc_train_iter'] = x
                
                data['acc_val_iter'] = x
                data['loss_val_iter'] = x
                data['f1_val_iter'] = x
                data['auc_val_iter'] = x

                data['acc_training_epoch'] = y
                data['loss_training_epoch'] = y
                data['f1_training_epoch'] = y
                data['auc_training_epoch'] = y
                
                data['acc_validation_epoch'] = y 
                data['loss_validation_epoch'] = y
                data['f1_validation_epoch'] = y
                data['auc_validation_epoch'] = y            

            train_dict[true_id] = data

        training_status = ''
        status = ''

        result_dict = {
            "iter": itr,
            "maxIter": max_itr,
            "epoch": epoch,
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            "trainingIterations": itr_trn,
            "trainDict": train_dict,
            "trainingStatus": training_status,  
            "status": status
        }
        return result_dict


if __name__ == "__main__":
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
        
