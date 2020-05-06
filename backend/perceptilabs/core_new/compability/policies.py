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
import cv2

def policy_regression(core, graphs, sanitized_to_name, sanitized_to_id, results):


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

    def get_layer_gradients(layer_id, true_id, graphs, results):
        data = {}
        
        if 'trainDict' in results:
            min_list = results['trainDict'][true_id]['Gradient']['Min'] 
            max_list = results['trainDict'][true_id]['Gradient']['Max']
            avg_list = results['trainDict'][true_id]['Gradient']['Average']
        else:
            min_list = []
            max_list = []
            avg_list = []
        
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

    def get_metrics(graphs, true_trn_id, results):
        data = {}
        x = np.random.random((60,)) # TODO: these are temporary whiel figuring out F1 and AUC
        y = np.random.random((10,))

        # ---- Get the metrics for ongoing epoch
        current_epoch = graphs[-1].active_training_node.layer.epoch

        if 'trainDict' in results:
            r_sq_trn_iter = results['trainDict'][true_trn_id]["r_sq_train_iter"] 
            loss_trn_iter = results['trainDict'][true_trn_id]["loss_train_iter"] 
            mse_trn_iter = results['trainDict'][true_trn_id]["mse_train_iter"] 
            sq_variance_trn_iter = results['trainDict'][true_trn_id]["sq_variance_train_iter"] 

            r_sq_val_iter = results['trainDict'][true_trn_id]["r_sq_validation_iter"] 
            loss_val_iter = results['trainDict'][true_trn_id]["loss_validation_iter"] 
            mse_val_iter = results['trainDict'][true_trn_id]["mse_validation_iter"] 
            sq_variance_val_iter = results['trainDict'][true_trn_id]["sq_variance_validation_iter"] 

            # inputs = results['trainDict'][true_trn_id]["inputs"] 
            # outputs = results['trainDict'][true_trn_id]["outputs"] 

        else:
            r_sq_trn_iter = []
            loss_trn_iter = []
            mse_trn_iter = []
            sq_variance_trn_iter = [] 

            r_sq_val_iter = [] 
            loss_val_iter = []
            mse_val_iter = []
            sq_variance_val_iter = []


        for graph in graphs:
            trn_layer = graph.active_training_node.layer
            if trn_layer.epoch == current_epoch and trn_layer.status == 'training':
                r_sq_trn_iter.append(trn_layer.r_squared_training)
                loss_trn_iter.append(trn_layer.loss_training)   
                mse_trn_iter.append(trn_layer.squared_error_training)              
                sq_variance_trn_iter.append(trn_layer.squared_variance_training) 
             

            if trn_layer.epoch == current_epoch and trn_layer.status == 'validation':
                r_sq_val_iter.append(trn_layer.r_squared_validation)
                loss_val_iter.append(trn_layer.loss_validation)   
                mse_val_iter.append(trn_layer.squared_error_validation)              
                sq_variance_val_iter.append(trn_layer.squared_variance_validation) 

            # inputs.append(trn_layer.inputs)
            # outputs.append(trn_layer.outputs)                   

        # ---- Get the metrics from the end of each epoch


        if 'trainDict' in results:
            r_sq_trn_epoch = results['trainDict'][true_trn_id]["r_sq_train_epoch"] 
            loss_trn_epoch = results['trainDict'][true_trn_id]["loss_train_epoch"] 
            mse_trn_epoch = results['trainDict'][true_trn_id]["mse_train_epoch"] 
            sq_variance_trn_epoch = results['trainDict'][true_trn_id]["sq_variance_train_epoch"] 

            r_sq_val_epoch = results['trainDict'][true_trn_id]["r_sq_validation_epoch"] 
            loss_val_epoch = results['trainDict'][true_trn_id]["loss_validation_epoch"] 
            mse_val_epoch = results['trainDict'][true_trn_id]["mse_validation_epoch"] 
            sq_variance_val_epoch = results['trainDict'][true_trn_id]["sq_variance_validation_epoch"] 

        else:
            r_sq_trn_epoch = []
            loss_trn_epoch = []
            mse_trn_epoch = []
            sq_variance_trn_epoch = [] 

            r_sq_val_epoch = [] 
            loss_val_epoch = []
            mse_val_epoch = []
            sq_variance_val_epoch = []

        idx = 1
        while idx < len(graphs):

            is_new_epoch = graphs[idx].active_training_node.layer.epoch != graphs[idx-1].active_training_node.layer.epoch
            #is_final_iteration = idx == len(graphs) - 1
            is_final_iteration = False

            if is_new_epoch or is_final_iteration:
                trn_layer = graphs[idx-1].active_training_node.layer                                                
                loss_trn_epoch.append(trn_layer.loss_training)
                r_sq_trn_epoch.append(trn_layer.r_squared_training)
                mse_trn_epoch.append(trn_layer.squared_error_training)
                sq_variance_trn_epoch.append(trn_layer.squared_variance_training)
                # TODO: f1 and auc train
                
                loss_val_epoch.append(trn_layer.loss_validation)
                r_sq_val_epoch.append(trn_layer.r_squared_validation)
                mse_val_epoch.append(trn_layer.squared_error_validation)
                sq_variance_val_epoch.append(trn_layer.squared_variance_validation)
                # TODO: f1 and auc val
            idx += 1

        # ---- Update the dicts
        data['loss_train_iter'] = loss_trn_iter
        data['r_sq_train_iter'] = r_sq_trn_iter
        data['mse_train_iter'] = mse_trn_iter
        data['sq_variance_train_iter'] = sq_variance_trn_iter
        
        data['loss_validation_iter'] = loss_val_iter
        data['r_sq_validation_iter'] = r_sq_val_iter
        data['mse_validation_iter'] = mse_val_iter
        data['sq_variance_validation_iter'] = sq_variance_val_iter       
                
        data['loss_train_epoch'] = loss_trn_epoch
        data['r_sq_train_epoch'] = r_sq_trn_epoch
        data['mse_train_epoch'] = mse_trn_epoch
        data['sq_variance_train_epoch'] = sq_variance_trn_epoch
        
        data['loss_validation_epoch'] = loss_val_epoch
        data['r_sq_validation_epoch'] = r_sq_val_epoch
        data['mse_validation_epoch'] = mse_val_epoch
        data['sq_variance_validation_epoch'] = sq_variance_val_epoch        

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
            data.update(get_layer_gradients(node.layer_id, true_id, graphs, results))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(graphs, true_trn_id, results))
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

        # import pdb
        # pdb.set_trace()
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

                    
            test_dict[true_id]['loss_validation_epoch'] = 0
            test_dict[true_id]['mse_validation_epoch'] = 0
            test_dict[true_id]['r_sq_validation_epoch'] = 0
            test_dict[true_id]['sq_variance_validation_epoch'] = 0

            test_dict[true_id]['loss_train_epoch'] = 0
            test_dict[true_id]['mse_train_epoch'] = 0
            test_dict[true_id]['r_sq_train_epoch'] = 0
            test_dict[true_id]['sq_variance_train_epoch'] = 0
                    
            test_dict[true_id]['loss_validation_iter'] = 0
            test_dict[true_id]['mse_validation_iter'] = 0
            test_dict[true_id]['r_sq_validation_iter'] = 0
            test_dict[true_id]['sq_variance_validation_iter'] = 0

            test_dict[true_id]['loss_train_iter'] = 0
            test_dict[true_id]['mse_train_iter'] = 0
            test_dict[true_id]['r_sq_train_iter'] = 0
            test_dict[true_id]['sq_variance_train_iter'] = 0

            test_dicts.append(test_dict)

        result_dict = {
            "maxTestIter": max_itr_tst,
            "testDicts": test_dicts,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }


        return result_dict

def policy_classification(core, graphs, sanitized_to_name, sanitized_to_id, results):


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

    def get_layer_gradients(layer_id, true_id, graphs, results):
        data = {}
        
        if 'trainDict' in results:
            min_list = results['trainDict'][true_id]['Gradient']['Min'] 
            max_list = results['trainDict'][true_id]['Gradient']['Max']
            avg_list = results['trainDict'][true_id]['Gradient']['Average']
        else:
            min_list = []
            max_list = []
            avg_list = []
        
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

    def get_metrics(graphs, true_trn_id, results):
        data = {}
        x = np.random.random((60,)) # TODO: these are temporary whiel figuring out F1 and AUC
        y = np.random.random((10,))

        # ---- Get the metrics for ongoing epoch
        current_epoch = graphs[-1].active_training_node.layer.epoch

        if 'trainDict' in results:
            acc_trn_iter = results['trainDict'][true_trn_id]["acc_train_iter"] 
            loss_trn_iter = results['trainDict'][true_trn_id]["loss_train_iter"] 
            f1_trn_iter = results['trainDict'][true_trn_id]["f1_train_iter"] 
            auc_trn_iter = results['trainDict'][true_trn_id]["auc_train_iter"] 

            acc_val_iter = results['trainDict'][true_trn_id]["acc_val_iter"] 
            loss_val_iter = results['trainDict'][true_trn_id]["loss_val_iter"] 
            f1_val_iter = results['trainDict'][true_trn_id]["f1_val_iter"] 
            auc_val_iter = results['trainDict'][true_trn_id]["auc_val_iter"] 

        else:
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

        if 'trainDict' in results:
            acc_trn_epoch = results['trainDict'][true_trn_id]["acc_training_epoch"]
            loss_trn_epoch = results['trainDict'][true_trn_id]["loss_training_epoch"] 
            f1_trn_epoch = results['trainDict'][true_trn_id]["f1_training_epoch"] 
            auc_trn_epoch = results['trainDict'][true_trn_id]["auc_training_epoch"] 

            acc_val_epoch = results['trainDict'][true_trn_id]["acc_validation_epoch"] 
            loss_val_epoch = results['trainDict'][true_trn_id]["loss_validation_epoch"] 
            f1_val_epoch = results['trainDict'][true_trn_id]["f1_validation_epoch"] 
            auc_val_epoch = results['trainDict'][true_trn_id]["auc_validation_epoch"] 
        else:
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
            data.update(get_layer_gradients(node.layer_id, true_id, graphs, results))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(graphs, true_trn_id, results))
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
        test_dicts = results.get('testDicts', []) # get existing
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

def policy_object_detection(core, graphs, sanitized_to_name, sanitized_to_id, results):
    
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

    def get_layer_gradients(layer_id, true_id, graphs, results):
        data = {}
        
        if 'trainDict' in results:
            min_list = results['trainDict'][true_id]['Gradient']['Min'] 
            max_list = results['trainDict'][true_id]['Gradient']['Max']
            avg_list = results['trainDict'][true_id]['Gradient']['Average']
        else:
            min_list = []
            max_list = []
            avg_list = []
        
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

    def iou(box1, box2):
     
        tb = min(box1[0] + 0.5 * box1[2], box2[0] + 0.5 * box2[2]) - \
            max(box1[0] - 0.5 * box1[2], box2[0] - 0.5 * box2[2])
        lr = min(box1[1] + 0.5 * box1[3], box2[1] + 0.5 * box2[3]) - \
            max(box1[1] - 0.5 * box1[3], box2[1] - 0.5 * box2[3])
        inter = 0 if tb < 0 or lr < 0 else tb * lr
        return inter / (box1[2] * box1[3] + box2[2] * box2[3] - inter)

    def plot_bounding_boxes(input_image, predicted_object, predicted_class, predicted_normalized_box):
        img_size = input_image.shape[0]
        predicted_box= predicted_normalized_box*img_size
        predicted_object = np.expand_dims(predicted_object, axis=-1)
        predicted_class = np.expand_dims(predicted_class, axis=-2)
        class_probs = predicted_object*predicted_class
        
        filter_mat_probs = np.array(class_probs >= 0.2, dtype='bool')
        filter_mat_boxes = np.nonzero(filter_mat_probs)
        boxes_filtered = predicted_box[filter_mat_boxes[0], filter_mat_boxes[1], filter_mat_boxes[2]]
        class_probs_filtered = class_probs[filter_mat_probs]
        
        classes_num_filtered = np.argmax(
            filter_mat_probs, axis=3)[
            filter_mat_boxes[0], filter_mat_boxes[1], filter_mat_boxes[2]]

        argsort = np.array(np.argsort(class_probs_filtered))[::-1]
        boxes_filtered = boxes_filtered[argsort]
        class_probs_filtered = class_probs_filtered[argsort]
        classes_num_filtered = classes_num_filtered[argsort]

        for i in range(len(boxes_filtered)):
            if class_probs_filtered[i] == 0:
                continue
            for j in range(i + 1, len(boxes_filtered)):
                if iou(boxes_filtered[i], boxes_filtered[j]) > 0.5:
                    class_probs_filtered[j] = 0.0
                    
        filter_iou = np.array(class_probs_filtered > 0.0, dtype='bool')
        boxes_filtered = boxes_filtered[filter_iou]
        class_probs_filtered = class_probs_filtered[filter_iou]
        classes_num_filtered = classes_num_filtered[filter_iou]

        result = []
        for i in range(len(boxes_filtered)):
            result.append(
                [classes_num_filtered[i],
                boxes_filtered[i][0],
                boxes_filtered[i][1],
                boxes_filtered[i][2],
                boxes_filtered[i][3],
                class_probs_filtered[i]])
        
        img = np.pad(input_image, [(50,50), (50,50), (0,0)], mode='constant', constant_values=255)
        for i in range(len(result)):
            x = int(result[i][1])+50
            y = int(result[i][2])+50
            w = int(result[i][3] / 2)
            h = int(result[i][4] / 2)
            cv2.rectangle(img, (x - w, y - h), (x + w, y + h), (231, 76, 60), 2)
            cv2.rectangle(img, (x - w, y - h - 20),
                        (x -w + 50, y - h), (46, 204, 113), -1)
            cv2.putText(
                img, '{} : {:.2f}'.format(result[i][0] ,result[i][5]),
                (x - w + 5, y - h - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                (0, 0, 0), 1, cv2.LINE_AA)
        return img, class_probs_filtered

    def get_metrics(graphs, true_trn_id, results):
        data = {}

        # ---- Get the metrics for ongoing epoch
        current_epoch = graphs[-1].active_training_node.layer.epoch

        if 'trainDict' in results:
            acc_trn_iter = results['trainDict'][true_trn_id]["acc_train_iter"] 
            loss_trn_iter = results['trainDict'][true_trn_id]["loss_train_iter"] 
            classification_loss_trn_iter = results['trainDict'][true_trn_id]["classification_loss_train_iter"] 
            bbox_loss_trn_iter = results['trainDict'][true_trn_id]["bboxes_loss_train_iter"] 
            
            acc_val_iter = results['trainDict'][true_trn_id]["acc_val_iter"] 
            loss_val_iter = results['trainDict'][true_trn_id]["loss_val_iter"] 
            classification_loss_val_iter = results['trainDict'][true_trn_id]["classification_loss_val_iter"] 
            bbox_loss_val_iter = results['trainDict'][true_trn_id]["bboxes_loss_val_iter"] 

        else:
            acc_trn_iter = []
            loss_trn_iter = []
            classification_loss_trn_iter =[]
            bbox_loss_trn_iter = []
            
            acc_val_iter = []
            loss_val_iter = []
            classification_loss_val_iter = []
            bbox_loss_val_iter = []

        predicted_objects = 0.
        predicted_classes = 0.
        predicted_normalized_boxes = 0.
        # confidence_scores = []
        image_accuracy = []

        for graph in graphs:
            trn_layer = graph.active_training_node.layer
            input_data_layer = trn_layer.get_input_data_node
            input_images = trn_node.layer.layer_outputs.get(input_data_layer)

            if trn_layer.epoch == current_epoch and trn_layer.status == 'training':
                acc_trn_iter.append(trn_layer.accuracy_training)
                loss_trn_iter.append(trn_layer.loss_training)                
                classification_loss_trn_iter.append(trn_layer.loss_classification_training)
                bbox_loss_trn_iter.append(trn_layer.loss_bbox_training)       
                predicted_objects = trn_layer.get_predicted_objects
                predicted_classes = trn_layer.get_predicted_classes
                predicted_normalized_boxes = trn_layer.get_predicted_normalized_boxes
                image_accuracy.append(trn_layer.image_accuracy)
            if trn_layer.epoch == current_epoch and trn_layer.status == 'validation':
                acc_val_iter.append(trn_layer.accuracy_validation)
                loss_val_iter.append(trn_layer.loss_validation)                
                classification_loss_val_iter.append(trn_layer.loss_classification_validation)
                bbox_loss_val_iter.append(trn_layer.loss_bbox_validation)   
                predicted_objects = trn_layer.get_predicted_objects
                predicted_classes = trn_layer.get_predicted_classes
                predicted_normalized_boxes = trn_layer.get_predicted_normalized_boxes
                image_accuracy.append(trn_layer.image_accuracy)
        
        # ---- Get the metrics from the end of each epoch
        if 'trainDict' in results:
            acc_trn_epoch = results['trainDict'][true_trn_id]["acc_training_epoch"]
            loss_trn_epoch = results['trainDict'][true_trn_id]["loss_training_epoch"] 
            classification_loss_trn_epoch = results['trainDict'][true_trn_id]["classification_loss_training_epoch"] 
            bbox_loss_trn_epoch = results['trainDict'][true_trn_id]["bboxes_loss_training_epoch"] 
            
            acc_val_epoch = results['trainDict'][true_trn_id]["acc_validation_epoch"] 
            loss_val_epoch = results['trainDict'][true_trn_id]["loss_validation_epoch"] 
            classification_loss_val_epoch = results['trainDict'][true_trn_id]["classification_loss_validation_epoch"] 
            bbox_loss_val_epoch = results['trainDict'][true_trn_id]["bboxes_loss_validation_epoch"] 
        else:
            acc_trn_epoch = []
            loss_trn_epoch = []
            classification_loss_trn_epoch = []
            bbox_loss_trn_epoch = []

            acc_val_epoch = []
            loss_val_epoch = []
            classification_loss_val_epoch = []
            bbox_loss_val_epoch = []
        
        idx = 1
        while idx < len(graphs):
            is_new_epoch = graphs[idx].active_training_node.layer.epoch != graphs[idx-1].active_training_node.layer.epoch
            #is_final_iteration = idx == len(graphs) - 1
            is_final_iteration = False

            if is_new_epoch or is_final_iteration:
                trn_layer = graphs[idx-1].active_training_node.layer                                                
                acc_trn_epoch.append(trn_layer.accuracy_training)
                loss_trn_epoch.append(trn_layer.loss_training)
                classification_loss_trn_epoch.append(trn_layer.loss_classification_training)
                bbox_loss_trn_epoch.append(trn_layer.loss_bbox_training)       
                
                acc_val_epoch.append(trn_layer.accuracy_validation)
                loss_val_epoch.append(trn_layer.loss_validation)
                classification_loss_val_epoch.append(trn_layer.loss_classification_validation)
                bbox_loss_val_epoch.append(trn_layer.loss_bbox_validation)
            idx += 1

        bbox_image, confidence_scores = plot_bounding_boxes(input_images[-1], predicted_objects, predicted_classes, predicted_normalized_boxes)
        
        # ---- Update the dicts
        
        data['loss_train_iter'] = loss_trn_iter
        data['classification_loss_train_iter'] = classification_loss_trn_iter
        data['bboxes_loss_train_iter'] = bbox_loss_trn_iter
        data['acc_train_iter'] = acc_trn_iter

        data['image_accuracy'] = image_accuracy

        data['acc_val_iter'] = acc_val_iter
        data['loss_val_iter'] = loss_val_iter
        data['classification_loss_val_iter'] = classification_loss_val_iter
        data['bboxes_loss_val_iter'] = bbox_loss_val_iter     
                
        data['acc_training_epoch'] = acc_trn_epoch
        data['loss_training_epoch'] = loss_trn_epoch
        data['classification_loss_training_epoch'] = classification_loss_trn_epoch
        data['bboxes_loss_training_epoch'] = bbox_loss_trn_epoch
        
        data['acc_validation_epoch'] = acc_val_epoch
        data['loss_validation_epoch'] = loss_val_epoch
        data['classification_loss_validation_epoch'] = classification_loss_val_epoch
        data['bboxes_loss_validation_epoch'] = bbox_loss_val_epoch      

        data['confidence_scores'] = confidence_scores
        data['image_bboxes'] =  bbox_image
        
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
            data.update(get_layer_gradients(node.layer_id, true_id, graphs, results))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(graphs, true_trn_id, results))
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
        test_dicts = results.get('testDicts', []) # get existing
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


            test_dict[true_id]['acc_validation_epoch'] = 0

            test_dict[true_id]['acc_train_iter'] = 0

            test_dict[true_id]['acc_val_iter'] = 0

            test_dicts.append(test_dict)

        result_dict = {
            "maxTestIter": max_itr_tst,
            "testDicts": test_dicts,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }


        return result_dict


def policy_reinforce(core, graphs, sanitized_to_name, sanitized_to_id, results):
    
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

    def get_layer_gradients(layer_id, true_id, graphs, results):
        data = {}
        
        if 'trainDict' in results:
            min_list = results['trainDict'][true_id]['Gradient']['Min'] 
            max_list = results['trainDict'][true_id]['Gradient']['Max']
            avg_list = results['trainDict'][true_id]['Gradient']['Average']
        else:
            min_list = []
            max_list = []
            avg_list = []
        
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

    def get_metrics(graphs, true_trn_id, results):
        data = {}
        # ---- Get the metrics for ongoing episode
        current_episode = graphs[-1].active_training_node.layer.episode

        if 'trainDict' in results:
            loss_trn_iter = results['trainDict'][true_trn_id]["loss_train_iter"] 
            reward_trn_iter = results['trainDict'][true_trn_id]["reward_train_iter"] 
        else:
            reward_trn_iter = []
            loss_trn_iter = []
    
        for graph in graphs:
            trn_layer = graph.active_training_node.layer
            # data_node = graph.data_nodes[0]
            state = trn_node.layer.transition['state_seq'][-1]
            steps = trn_node.layer.step_counter
            n_actions = trn_node.layer.n_actions
            current_action = trn_node.layer.transition['action']
            probs = trn_node.layer.transition['probs']
            if n_actions != -1 and current_action != -1:
                pred = np.zeros((n_actions,))
                pred[int(current_action)] = 1
            
            if trn_layer.episode == current_episode and trn_layer.status == 'training':
                reward_trn_iter.append(trn_layer.reward)
                loss_trn_iter.append(trn_layer.loss_training)                                      

        # ---- Get the metrics from the end of each episode

        if 'trainDict' in results:
            reward_trn_episode = results['trainDict'][true_trn_id]["reward_training_episode"]
            loss_trn_episode = results['trainDict'][true_trn_id]["loss_training_episode"] 
    
        else:
            reward_trn_episode = []
            loss_trn_episode = []


        idx = 1
        while idx < len(graphs):
            is_new_episode = graphs[idx].active_training_node.layer.episode != graphs[idx-1].active_training_node.layer.episode
            #is_final_iteration = idx == len(graphs) - 1
            is_final_iteration = False

            if is_new_episode or is_final_iteration:
                trn_layer = graphs[idx-1].active_training_node.layer                                                
                reward_trn_episode.append(np.sum(reward_trn_iter))
                loss_trn_episode.append(trn_layer.loss_training)

            idx += 1

        # ---- Update the dicts
        data['reward_train_iter'] = reward_trn_iter
        data['loss_train_iter'] = loss_trn_iter
                
        data['reward_training_episode'] = reward_trn_episode
        data['loss_training_episode'] = loss_trn_episode
        data['Steps'] = steps
        data['state'] = state
        data['probs'] = probs
        data['pred'] = pred
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
            data.update(get_layer_gradients(node.layer_id, true_id, graphs, results))
            train_dict[true_id] = data

        # ----- Get data specific to the training layer.
        data = {}        
        true_trn_id = sanitized_to_id[trn_node.layer_id]
        data.update(get_metrics(graphs, true_trn_id, results))
        train_dict[true_trn_id].update(data)

        # itr = 0
        # max_itr = 0
        epoch = 0
        # max_epoch = -1
        itr_trn = 0
        max_itr_trn = -1
        max_itr_val = -1
        max_itr = -1

        batch_size = trn_node.layer.batch_size
        itr = trn_node.layer.step_counter
        max_iter = trn_node.layer.n_steps_max
        max_epoch = trn_node.layer.n_episodes

                    
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
            "maxIter": max_iter,
            "epoch": epoch,
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            "trainingIterations": trn_node.layer.step_counter,
            "trainDict": train_dict,
            "trainingStatus": training_status,  
            "status": status,
            "progress": trn_node.layer.progress
        }
        return result_dict

    