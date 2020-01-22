import dill
import tensorflow as tf
from typing import List, Callable
from core_new.layers import DataLayer, TrainingLayer, Tf1xLayer


class DataLayerReplica(DataLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._variables = variables

    @property
    def sample(self):
        return dill.loads(self._sample)

    @property
    def size_training(self):
        return dill.loads(self._size_training)        

    @property
    def size_validation(self):
        return dill.loads(self._size_validation)                

    @property
    def size_testing(self):
        return dill.loads(self._size_testing)                        
        return self._client.read(self._identifier, 'size_testing')                

    @property        
    def variables(self):
        return dill.loads(self._variables)                                

    def make_generator_training(self):
        raise NotImplementedError

    def make_generator_validation(self):
        raise NotImplementedError        

    def make_generator_testing(self):
        raise NotImplementedError

    
    

    
class Tf1xClassificationLayerReplica(TrainingLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation,
                 loss_training, loss_testing, loss_validation, status):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._variables = variables
        self._accuracy_training = accuracy_training
        self._accuracy_validation = accuracy_validation
        self._accuracy_testing = accuracy_testing        
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing        

    
    @property
    def sample(self):
        return dill.loads(self._sample)

    @property
    def size_training(self):
        return dill.loads(self._size_training)        

    @property
    def size_validation(self):
        return dill.loads(self._size_validation)                

    @property
    def size_testing(self):
        return dill.loads(self._size_testing)                        
        return self._client.read(self._identifier, 'size_testing')                

    @property        
    def variables(self):
        return dill.loads(self._variables)                                

    @property
    def accuracy_training(self):
        return dill.loads(self._accuracy_training)

    @property
    def accuracy_testing(self):
        return dill.loads(self._accuracy_testing)

    @property
    def accuracy_validation(self):
        return dill.loads(self._accuracy_validation)

    @property
    def loss_training(self):
        return dill.loads(self._loss_training)

    @property
    def loss_testing(self):
        return dill.loads(self._loss_testing)

    @property
    def loss_validation(self):
        return dill.loads(self._loss_validation)
        
    @property
    def status(self):
        return dill.loads(self._status)       
    
    def make_generator_training(self):
        raise NotImplementedError

    def make_generator_validation(self):
        raise NotImplementedError        

    def make_generator_testing(self):
        raise NotImplementedError
    
    def on_pause(self):
        raise NotImplementedError        

    
        
class Tf1xLayerReplica(BaseReplica, Tf1xLayer):
    def __init__(self, variables, trainable_variables):
        self._variables = variables
        self._trainable_variables = trainable_variables
    
    @property
    def trainable_variables(self):
        return dill.loads(self._trainable_variables)                               

    @property        
    def variables(self):
        return dill.loads(self._variables)
    
    @property        
    def trainable_variables(self):
        return dill.loads(self._trainable_variables)                                

    def __call__(self, x: tf.Tensor):
        raise NotImplementedError        

    def __call__(self, x: List[tf.Tensor]):
        raise NotImplementedError                
    
