from abc import ABC, abstractmethod
import numpy as np

class DataPolicy(ABC):
    def __init__(self, session, data_dict, graph_dict):
        self._session = session
        self._data = data_dict
        self._graph_dict = graph_dict
    
    @abstractmethod
    def get_results(self):
        raise NotImplementedError

    
class TestDataPolicy(DataPolicy):
    def get_results(self):
        test_dict = {}

        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                test_dict[id_]={}
                itr_tst = self._data[id_].get('iter_testing', 0)
     
                max_itr_tst = self._data[id_].get('max_iter_testing', -1)

                test_dict[id_]['acc_training_epoch'] = 0
                test_dict[id_]['f1_training_epoch'] = 0
                test_dict[id_]['auc_training_epoch'] = 0
                
                test_dict[id_]['acc_validation_epoch'] = 0
                test_dict[id_]['f1_validation_epoch'] = 0
                test_dict[id_]['auc_validation_epoch'] = 0

                test_dict[id_]['acc_train_iter'] = 0
                test_dict[id_]['f1_train_iter'] = 0
                test_dict[id_]['auc_train_iter'] = 0
                
                test_dict[id_]['acc_val_iter'] = 0
                test_dict[id_]['f1_val_iter'] = 0
                test_dict[id_]['auc_val_iter'] = 0

                if "all_tensors" in self._data[id_]:
                    all_tensors=self._data[id_]["all_tensors"]

                    import collections
                    import six
                    def update(d, u):
                        for k, v in six.iteritems(u):
                            dv = d.get(k, {})
                            if not isinstance(dv, collections.Mapping):
                                d[k] = v
                            elif isinstance(v, collections.Mapping):
                                d[k] = update(dv, v)
                            else:
                                d[k] = v
                        return d

                    test_dict=update(test_dict,all_tensors)
        training_status = 'Finished'
        status='Running'
        test_status='Waiting'
        
        result_dict = {
            "maxTestIter": max_itr_tst,
            "testDict": test_dict,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }
        return result_dict
    
class TrainValDataPolicy(DataPolicy):
    def get_results(self):
        train_dict = {}
        saver=None

        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                train_dict[id_]={}
                epoch = self._data[id_].get('epoch', 0)        
                itr_trn = self._data[id_].get('iter_training', 0)
                itr_val = self._data[id_].get('iter_validation', 0)

                if "saver" in self._data:
                    saver = self._data.pop('saver', None)
                if saver:
                    sess=saver[0]
                    tf_saver=saver[1]
                    network_outputs=self._data[id_].get("y_pred",None)
                    input_id=None
                    tmp_content=self._graph_dict[[i for i in content["Info"]["backward_connections"] if i!=self._graph_dict[content["Info"]["Properties"]["Labels"]]][0]]
                    while tmp_content["Info"]["backward_connections"]!=[]:
                        input_id=tmp_content["Info"]["backward_connections"][0]
                        tmp_content=self._graph_dict[input_id]
                    network_inputs=self._data[input_id]["Y"]
                    saver={"sess":sess, "saver":tf_saver, "network_inputs":network_inputs, "network_outputs": network_outputs}
                    if "all_tensors" in self._data[id_]:
                        saver.update({"all_tensors":self._data[id_]["all_tensors"]})

                max_epoch = self._data[id_].get('max_epoch', -1)        
                train_datasize = self._data[id_].get('train_datasize', -1)
                val_datasize = self._data[id_].get('val_datasize', -1)

                train_dict[id_]['acc_training_epoch'] = self._data[id_].get('acc_training_epoch', [-1])
                train_dict[id_]['loss_training_epoch'] = self._data[id_].get('loss_training_epoch', [-1])
                train_dict[id_]['f1_training_epoch'] = self._data[id_].get('f1_training_epoch', [-1])
                train_dict[id_]['auc_training_epoch'] = self._data[id_].get('auc_training_epoch', [-1])
                
                train_dict[id_]['acc_validation_epoch'] = self._data[id_].get('acc_validation_epoch', [-1])
                train_dict[id_]['loss_validation_epoch'] = self._data[id_].get('loss_validation_epoch', [-1])
                train_dict[id_]['f1_validation_epoch'] = self._data[id_].get('f1_validation_epoch', [-1])
                train_dict[id_]['auc_validation_epoch'] = self._data[id_].get('auc_validation_epoch', [-1])

                train_dict[id_]['acc_train_iter'] = self._data[id_].get('acc_train_iter', [-1])
                train_dict[id_]['loss_train_iter'] = self._data[id_].get('loss_train_iter', [-1])
                train_dict[id_]['f1_train_iter'] = self._data[id_].get('f1_train_iter', [-1])
                train_dict[id_]['auc_train_iter'] = self._data[id_].get('auc_train_iter', [-1])
                
                train_dict[id_]['acc_val_iter'] = self._data[id_].get('acc_val_iter', [-1])
                train_dict[id_]['loss_val_iter'] = self._data[id_].get('loss_val_iter', [-1])
                train_dict[id_]['f1_val_iter'] = self._data[id_].get('f1_val_iter', [-1])
                train_dict[id_]['auc_val_iter'] = self._data[id_].get('auc_val_iter', [-1])
                if "all_evaled_tensors" in self._data[id_]:
                    all_evaled_tensors=self._data[id_]["all_evaled_tensors"]

                    import collections
                    import six
                    def update(d, u):
                        for k, v in six.iteritems(u):
                            dv = d.get(k, {})
                            if not isinstance(dv, collections.Mapping):
                                d[k] = v
                            elif isinstance(v, collections.Mapping):
                                d[k] = update(dv, v)
                            else:
                                d[k] = v
                        return d

                    train_dict=update(train_dict,all_evaled_tensors)
                if not self._session._headless:
                    for key, value in self._data[id_].items():
                        if not key.startswith('grad-weights-'):
                            continue
                        grad_layer_id = key[len('grad-weights-'):].split(':')[0]

                        if grad_layer_id not in train_dict:
                            train_dict[grad_layer_id] = {}
                        if 'Gradient' not in train_dict[grad_layer_id]:
                            train_dict[grad_layer_id]['Gradient']={}
                        
                        if key.split(':')[2]=="Min":
                            train_dict[grad_layer_id]['Gradient']['Min'] = value
                        elif key.split(':')[2]=="Max":
                            train_dict[grad_layer_id]['Gradient']['Max'] = value
                        elif key.split(':')[2]=="Average":
                            train_dict[grad_layer_id]['Gradient']['Average'] = value

            if content["Info"]["Type"] in ["DataData", "DataEnvironment"]:
                batch_size = self._data[id_].get('batch_size', -1)

        # Set up variables to mimic FSM:
        itr = itr_trn + itr_val
        #Dividing with batch_size to get the actuall iterations it will run rather than 
        max_itr_trn=train_datasize/batch_size
        max_itr_val=val_datasize/batch_size

        max_itr = max_itr_trn + max_itr_val

        # Initial values
        training_status = 'Waiting'
        status = 'Created'

        # LOGIC
        if epoch < max_epoch: 
            # Training/validation modes

            if itr < max_itr_trn:
                training_status = 'Training'
            else:
                training_status = 'Validation'

            if self._session.is_paused:
                status = 'Paused'
            else:
                status = 'Running' 
        else:
            if itr >= max_itr_trn-1:
                training_status='Finished'    
        
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
        if saver is not None:
            result_dict["saver"]=saver
        return result_dict


class TrainReinforceDataPolicy(DataPolicy):
    def get_results(self):
        train_dict = {}
       
        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            if content["Info"]["Type"] == "TrainReinforce":
                step_counter = self._data[id_].get('step_counter', -1)
                n_steps_max = self._data[id_].get('n_steps_max', -1)                
                episode = self._data[id_].get('episode', -1)
                n_episodes = self._data[id_].get('n_episodes', -1)
                batch_size = self._data[id_].get('batch_size', -1)                                

                train_dict[id_] = {}
                train_dict[id_]['state'] = self._data[id_].get('current_state', -1)
                state__ = train_dict[id_]['state']
                #print("CURRENT STATE READ IN POLICY")
                #print(train_dict[id_]['state'])

                current_action = self._data[id_].get('current_action', -1)
                n_actions = self._data[id_].get('n_actions', -1)
                if n_actions != -1 and current_action != -1:
                    train_dict[id_]['pred'] = np.zeros((n_actions,))
                    train_dict[id_]['pred'][int(current_action)] = 1

                train_dict[id_]['X'] = {}
                train_dict[id_]['X']['Reward'] = self._data[id_].get('reward', [-1])
                train_dict[id_]['X']['epochTotalReward'] = self._data[id_].get('episode_reward', [-1])
                train_dict[id_]['X']['epochTotalSteps'] = self._data[id_].get('episode_steps', [-1])


                train_dict[id_]['loss'] = self._data[id_].get('loss', [-1])
                train_dict[id_]['epochTrainLoss'] = self._data[id_].get('episode_loss', [-1])


                if "all_tensors" in self._data[id_]:
                    # all_tensors=train_dict[id_].pop("all_tensors")
                    all_tensors=self._data[id_]["all_tensors"]

                    import collections
                    import six
                    def update(d, u):
                        for k, v in six.iteritems(u):
                            dv = d.get(k, {})
                            if not isinstance(dv, collections.Mapping):
                                d[k] = v
                            elif isinstance(v, collections.Mapping):
                                d[k] = update(dv, v)
                            else:
                                d[k] = v
                        return d

                    train_dict=update(train_dict,all_tensors)

                
                if not self._session._headless:
                    for key, value in self._data[id_].items():
                        if not key.startswith('grad-weights-'):
                            continue
                        grad_layer_id = key[len('grad-weights-'):].split(':')[0]
                        
                        if grad_layer_id not in train_dict:
                            train_dict[grad_layer_id] = {}
                        if 'Gradient' not in train_dict[grad_layer_id]:
                            train_dict[grad_layer_id]['Gradient']={}
                        
                        if key.split(':')[2]=="Min":
                            train_dict[grad_layer_id]['Gradient']['Min'] = value
                        elif key.split(':')[2]=="Max":
                            train_dict[grad_layer_id]['Gradient']['Max'] = value
                        elif key.split(':')[2]=="Average":
                            train_dict[grad_layer_id]['Gradient']['Average'] = value

                        ## Gradients are only defined for the target network.
                        #copied_id = self._graph_dict[grad_layer_id].get('CopyOf')
                        #if copied_id is not None:
                        #    if copied_id not in train_dict:
                        #        train_dict[copied_id] = {}                                                    
                        #    train_dict[copied_id]['Gradient'] = train_dict[grad_layer_id]['Gradient'].copy()

       
        for id_, content in self._graph_dict.items():
            if content["Info"]["Type"] == "DataEnvironment":
                train_dict[id_] = {'state': state__}
                break
                
                
        training_status = 'Training'
        status = 'Running'
        itr_trn = 123

        import pprint
        #print("train_dict")
        #pprint.pprint(train_dict)
        
 
        result_dict = {
            "iter": step_counter,
            "maxIter": n_steps_max,
            "epoch": episode,
            "maxEpochs": n_episodes,
            "batch_size": batch_size,
            "trainingIterations": itr_trn,
            "trainDict": train_dict,
            "trainingStatus": training_status,  
            "status": status
        }
        return result_dict

