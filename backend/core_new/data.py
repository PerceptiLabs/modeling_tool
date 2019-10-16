import copy
from abc import ABC, abstractmethod

class DataContainer:
    def __init__(self):
        self.reset()

    def reset(self):
        self._data_dict = dict()        

    def _create_subdict_if_needed(self, layer_id):
        if not layer_id in self._data_dict:
            self._data_dict[layer_id] = dict()

    def store_value_in_root(self, name, value):
        self._data_dict[name] = value

    def store_value(self, layer_id, name, value):
        self._create_subdict_if_needed(layer_id)
        self._data_dict[layer_id][name] = value

    def stack_value(self, layer_id, name, value):
        self._create_subdict_if_needed(layer_id)

        try:
            self._data_dict[layer_id][name].append(value)
            if len(self._data_dict[layer_id][name])>500:
                self._data_dict[layer_id][name].pop(0)
        except AttributeError:
            print("warning, overwriting existing value!")
            self._data_dict[layer_id][name] = [value]
        except KeyError:
            self._data_dict[layer_id][name] = [value]

    def evaluate_dict(self, d):
        import tensorflow as tf
        if type(d) is dict:
            new_d={}
            for key, value in d.items():
                new_d[key] = self.evaluate_dict(value)
                if new_d[key] is None or new_d[key]=={}:
                    new_d.pop(key)
            return new_d

        if tf.contrib.framework.is_tensor(d):
            return d

    def on_tensors_get(self):
        return self.evaluate_dict(self.to_dict())

    def __getitem__(self, id_):
        data = copy.copy(self._data_dict.get(id_))
        return data

    def __contains__(self, id_):
        return id_ in self._data_dict

    def to_dict(self):
        data_dict = copy.copy(self._data_dict)
        return data_dict

    
class DataPolicy(ABC):
    @abstractmethod
    def get_results(self):
        raise NotImplementedError

class TestDataPolicy:
    def __init__(self, session, data_dict, graph_dict):
        self._session = session
        self._data = data_dict
        self._graph_dict = graph_dict

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
    
class TrainValDataPolicy:
    def __init__(self, session, data_dict, graph_dict):
        self._session = session
        self._data = data_dict
        self._graph_dict = graph_dict

    def get_results(self):
        train_dict = {}

        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                train_dict[id_]={}
                epoch = self._data[id_].get('epoch', 0)        
                itr_trn = self._data[id_].get('iter_training', 0)
                itr_val = self._data[id_].get('iter_validation', 0)

                max_epoch = self._data[id_].get('max_epoch', -1)        
                max_itr_trn = self._data[id_].get('max_iter_training', -1)
                max_itr_val = self._data[id_].get('max_iter_validation', -1)

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

            if content["Info"]["Type"] in ["DataData", "DataEnvironment"]:
                batch_size = self._data[id_].get('batch_size', -1)

        # Set up variables to mimic FSM:
        itr = itr_trn + itr_val
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
        return result_dict