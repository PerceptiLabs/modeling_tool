import copy

####################################################################
# Conversion needed to comply with format. If we generalize frontend
# so that it uses a specification for each dashboard, we could
# send the data_container.to_dict() as is and the frontend could
# simply extract whatever it needs from it.
####################################################################        

class ResultDictMaker:
    def __init__(self, data_dict, graph_dict, dashboard, flags):
        self._data = data_dict
        self._graph_dict = graph_dict

    def _get_training_layer_id(self):
        # TODO: this is a hack and wont work with several training layers
        for id_, content in self._graph_dict.items():
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                return id_
        return None
    
    def _get_data_layer_id(self):
        # TODO: this is a hack and wont work with several training layers
        for id_, content in self._graph_dict.items():
            if content["Info"]["Type"] in ["DataData", "DataEnvironment"]:
                return id_
        return None
        
    def make(self):
        train_dict = {}
        test_dict = {}
        
        #for id_ in self._graph_dict.keys():
        #    train_dict[id_] = {}
        #    test_dict[id_] = {}            


        for id_, content in self._graph_dict.items():
            if id_ not in self._data:
                continue
            
            #import pprint
            #pprint.pprint(self._data[id_])
        
            if content["Info"]["Type"] in ["TrainNormal", "TrainReinforce"]:
                epoch_list = self._data[id_].get('epoch', [-1])        
                itr_trn_list = self._data[id_].get('iter_training', [-1])
                itr_val_list = self._data[id_].get('iter_validation', [-1])
                itr_tst_list = self._data[id_].get('iter_testing', [0])

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


                for key, value in self._data[id_].items():
                    if not key.startswith('grad-weights-'):
                        continue

                    grad_layer_id = key[len('grad-weights-'):].split(':')[0]

                    if grad_layer_id not in train_dict:
                        train_dict[grad_layer_id] = {}
                    if grad_layer_id not in test_dict:
                        test_dict[grad_layer_id] = {}
                    
                    train_dict[grad_layer_id]['Gradient'] = value[-1] # LATEST GRADIENTS
                    test_dict[grad_layer_id]['Gradient'] = value[-1]                                

            if content["Info"]["Type"] in ["DataData", "DataEnvironment"]:
                batch_size = self._data[id_].get('batch_size', -1)
        
        
        result_dict = {
            "iter": itr_trn_list[-1] + itr_val_list[-1],
            "maxIter": max_itr_trn + max_itr_val,
            "epoch": epoch_list[-1],
            "maxEpochs": max_epoch,
            "batch_size": batch_size,
            "graphObj": {},#copy.copy(self._graph_dict),
            "trainingIterations": itr_trn_list[-1],
            "trainDict": train_dict,
            "testIter": itr_tst_list[-1],
            "maxTestIter": max_itr_tst,
            "testDict": test_dict,
            "trainingStatus": "",
            "testStatus": "",           
            "status": ""
        }
        return result_dict


    

