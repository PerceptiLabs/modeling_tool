# WARNING:
#
#     JsonNetwork comes with fields 'Id' and 'Name'.
#     Graph nodes have a field called 'layer_id', which is a sanitized version of 'Name' [remove spaces]
#
#     Therefore we use the mappings called 'sanitized_to_name' and 'sanitized_to_id'
#     so that we can take the sanitized name (i.e., node.layer_id) and find the original JsonNetwork 'Name' and 'Id'.
#
# TODO: fix the above to avoid confusion.

import numpy as np


def policy_classification(core, graphs, sanitized_to_name, sanitized_to_id):

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

    test_graphs = []
    for graph in graphs:
        if graph.active_training_node.layer.status == 'testing':
            test_graphs.append(graph)
    
    if len(test_graphs)==0:
        trn_node = current_graph.active_training_node
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

        if core.is_paused:
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
        test_dicts = []
        for current_graph in test_graphs:
            trn_node = current_graph.active_training_node
            test_dict = {}
            for node in current_graph.nodes:
                data = {}
                true_id = sanitized_to_id[node.layer_id] # nodes use spec names for layer ids
                data.update(get_layer_inputs_and_outputs(current_graph, node, trn_node))
                test_dict[true_id] = data
            
            training_status = 'Finished'
            status='Running'
            test_status='Waiting'

            # if trn_node.layer.size_testing and trn_node.layer.batch_size:
            max_itr_tst = trn_node.layer.size_testing

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

            test_dicts.append(test_dict)

        result_dict = {
            "maxTestIter": max_itr_tst,
            "testDicts": test_dicts,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }


        return result_dict


