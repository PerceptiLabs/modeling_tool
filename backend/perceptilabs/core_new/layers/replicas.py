import dill
import tensorflow as tf
from typing import List, Callable

from perceptilabs.core_new.layers import DataLayer, TrainingLayer, Tf1xLayer


class DataLayerReplica(DataLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._variables = variables

    @property
    def sample(self):
        return dill.loads(self._sample) if self._sample is not None else None

    @property
    def size_training(self):
        return dill.loads(self._size_training) if self._size_training is not None else None      

    @property
    def size_validation(self):
        return dill.loads(self._size_validation) if self._size_validation is not None else None                

    @property
    def size_testing(self):
        return dill.loads(self._size_testing) if self._size_testing is not None else None                        

    @property        
    def variables(self):
        return dill.loads(self._variables) if self._variables is not None else None                                
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
        return dill.loads(self._sample) if self._sample is not None else None

    @property
    def size_training(self):
        return dill.loads(self._size_training) if self._size_training is not None else None        

    @property
    def size_validation(self):
        return dill.loads(self._size_validation) if self._size_validation is not None else None

    @property
    def size_testing(self):
        return dill.loads(self._size_testing) if self._size_testing is not None else None                        

    @property        
    def variables(self):
        return dill.loads(self._variables) if self._variables is not None else None                                

    @property
    def accuracy_training(self):
        return dill.loads(self._accuracy_training) if self._accuracy_training is not None else None

    @property
    def accuracy_testing(self):
        return dill.loads(self._accuracy_testing) if self._accuracy_testing is not None else None

    @property
    def accuracy_validation(self):
        return dill.loads(self._accuracy_validation) if self._accuracy_validation is not None else None

    @property
    def loss_training(self):
        return dill.loads(self._loss_training) if self._loss_training is not None else None

    @property
    def loss_testing(self):
        return dill.loads(self._loss_testing) if self._loss_testing is not None else None

    @property
    def loss_validation(self):
        return dill.loads(self._loss_validation) if self._loss_validation is not None else None
        
    @property
    def status(self):
        return dill.loads(self._status) if self._status is not None else None       
    
    def make_generator_training(self):
        raise NotImplementedError

    def make_generator_validation(self):
        raise NotImplementedError        

    def make_generator_testing(self):
        raise NotImplementedError
    
    def on_pause(self):
        raise NotImplementedError        

    
        
class Tf1xLayerReplica(Tf1xLayer):
    def __init__(self, variables, trainable_variables):
        self._variables = variables
        self._trainable_variables = trainable_variables
    
    @property
    def trainable_variables(self):
        return dill.loads(self._trainable_variables) if self._trainable_variables is not None else None                               

    @property        
    def variables(self):
        return dill.loads(self._variables) if self._variables is not None else None
    
    @property        
    def trainable_variables(self):
        return dill.loads(self._trainable_variables) if self._trainable_variables is not None else None                                

    def __call__(self, x: tf.Tensor):
        raise NotImplementedError        

    def __call__(self, x: List[tf.Tensor]):
        raise NotImplementedError                
    
