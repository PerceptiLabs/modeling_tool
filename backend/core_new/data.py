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

class Evaluator:
    def set_sess(self,sess):
        self.sess=sess

    def eval(self,variable):
        import tensorflow as tf
        if self.sess and tf.contrib.framework.is_tensor(variable):
            return self.sess.run(variable)
        else:
            return variable
    
    
class TrainValTestDataPolicy:
    def __init__(self, session, data_dict, graph_dict):
        self._session = session
        self._data = data_dict
        self._graph_dict = graph_dict

    def evaluate_dict(self, d, evaluator):
        if type(d) is dict:
            new_d={}
            for key, value in d.items():
                new_d[key] = self.evaluate_dict(value, evaluator)
            return new_d

        return evaluator.eval(d)

    def get_results(self):
        train_dict = {}
        #test_dict = {}

        if not self._session._headless:
            evaluator = Evaluator()
            sess=self._data.pop("sess", None)
            if sess:
                evaluator.set_sess(sess)
            train_dict = self.evaluate_dict(self._data,evaluator)

        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                epoch = self._data[id_].get('epoch', 0)        
                itr_trn = self._data[id_].get('iter_training', 0)
                itr_val = self._data[id_].get('iter_validation', 0)
                itr_tst = self._data[id_].get('iter_testing', 0)

                max_epoch = self._data[id_].get('max_epoch', -1)        
                max_itr_trn = self._data[id_].get('max_iter_training', -1)
                max_itr_val = self._data[id_].get('max_iter_validation', -1)
                max_itr_tst = self._data[id_].get('max_iter_testing', -1)


                train_dict['epochTrainAccuracy'] = self._data[id_].get('acc_training_epoch', [-1])
                train_dict['epochTrainF1'] = self._data[id_].get('f1_training_epoch', [-1])
                train_dict['epochTrainAUC'] = self._data[id_].get('auc_training_epoch', [-1])
                
                train_dict['epochValAccuracy'] = self._data[id_].get('acc_validation_epoch', [-1])
                train_dict['epochValF1'] = self._data[id_].get('f1_validation_epoch', [-1])
                train_dict['epochValAUC'] = self._data[id_].get('auc_validation_epoch', [-1])

                if not self._session._headless:
                    for key, value in self._data[id_].items():
                        if not key.startswith('grad-weights-'):
                            continue
                        grad_layer_id = key[len('grad-weights-'):].split(':')[0]

                        if grad_layer_id not in train_dict:
                            train_dict[grad_layer_id] = {}
                        if 'Gradient' not in train_dict[grad_layer_id]:
                            train_dict[grad_layer_id]['Gradient']={}
                        #if grad_layer_id not in test_dict:
                        #    test_dict[grad_layer_id] = {}
                        
                        if key.split(':')[2]=="Min":
                            train_dict[grad_layer_id]['Gradient']['Min'] = value
                        elif key.split(':')[2]=="Max":
                            train_dict[grad_layer_id]['Gradient']['Max'] = value
                        elif key.split(':')[2]=="Average":
                            train_dict[grad_layer_id]['Gradient']['Average'] = value
                        # test_dict[grad_layer_id]['Gradient'] = value[-1] 

            if content["Info"]["Type"] in ["DataData", "DataEnvironment"]:
                batch_size = self._data[id_].get('batch_size', -1)


        # Set up variables to mimic FSM:
        itr = itr_trn + itr_val
        max_itr = max_itr_trn + max_itr_val

        # Initial values
        training_status = 'Waiting'
        test_status = 'First'
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
            # Testing mode
            training_status = 'Finished'

            if itr_tst < max_itr_tst:
                test_status = 'Running'
            else:
                # TODO: should it be smth like "Finished" now? Since we will
                # now run all test iterations and THEN send all results to coreLogic [for previous/next view etc]
                test_status = 'Waiting' 
                
            if self._session.is_paused:
                status = 'Paused'
            else:
                status = 'Done training'            
        
        result_dict = {
            "iter": itr,
            "maxIter": max_itr,
            "epoch": epoch,
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            # "graphObj": copy.copy(self._graph_dict),
            "trainingIterations": itr_trn,
            "trainDict": train_dict,
            "testIter": itr_tst,
            "maxTestIter": max_itr_tst,
            # "testDict": test_dict,
            "trainingStatus": training_status,
            "testStatus": test_status,           
            "status": status
        }
        return result_dict


    
    
