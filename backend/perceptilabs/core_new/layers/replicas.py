import dill
import tensorflow as tf
from typing import List, Callable

from perceptilabs.core_new.layers import DataLayer, TrainingLayer, Tf1xLayer, Tf1xClassificationLayer


class DataLayerReplica(DataLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._variables = variables

    @property
    def sample(self):
        return self._sample if self._sample is not None else None

    @property
    def size_training(self):
        return self._size_training if self._size_training is not None else None      

    @property
    def size_validation(self):
        return self._size_validation if self._size_validation is not None else None                

    @property
    def size_testing(self):
        return self._size_testing if self._size_testing is not None else None                        

    @property        
    def variables(self):
        return self._variables if self._variables is not None else None                                
    def make_generator_training(self):
        raise NotImplementedError

    def make_generator_validation(self):
        raise NotImplementedError        

    def make_generator_testing(self):
        raise NotImplementedError

    
class Tf1xClassificationLayerReplica(Tf1xClassificationLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation,
                 loss_training, loss_testing, loss_validation, status, layer_weights, layer_gradients, layer_outputs):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._variables = variables or {}
        self._accuracy_training = accuracy_training or []
        self._accuracy_validation = accuracy_validation or []
        self._accuracy_testing = accuracy_testing or []
        self._loss_training = loss_training or []
        self._loss_validation = loss_validation or []
        self._loss_testing = loss_testing or []
        self._status = status

        self._layer_weights = layer_weights or {}
        self._layer_gradients = layer_gradients or {}
        self._layer_outputs = layer_outputs or {}

        
    @property
    def sample(self):
        return self._sample 

    @property
    def size_training(self):
        return self._size_training 

    @property
    def size_validation(self):
        return self._size_validation

    @property
    def size_testing(self):
        return self._size_testing 

    @property        
    def variables(self):
        return self._variables 

    @property
    def accuracy_training(self):
        return self._accuracy_training

    @property
    def accuracy_testing(self):
        return self._accuracy_testing

    @property
    def accuracy_validation(self):
        return self._accuracy_validation

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def loss_testing(self):
        return self._loss_testing

    @property
    def loss_validation(self):
        return self._loss_validation
        
    @property
    def status(self):
        return self._status

    @property
    def layer_weights(self):
        return self._layer_weights
    
    @property
    def layer_gradients(self):
        return self._layer_gradients
    
    @property
    def layer_outputs(self):
        return self._layer_outputs

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
        return self._trainable_variables if self._trainable_variables is not None else None          

    @property        
    def variables(self):
        return self._variables if self._variables is not None else None
    
    @property        
    def trainable_variables(self):
        return self._trainable_variables if self._trainable_variables is not None else None                                
    def __call__(self, x: tf.Tensor):
        raise NotImplementedError        

    def __call__(self, x: List[tf.Tensor]):
        raise NotImplementedError                
    
