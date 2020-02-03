""" These classes serve as interfaces for code generated from templates """


from abc import ABC, abstractmethod
from typing import Dict, Any, overload, List
import tensorflow as tf

#from core_new.graph import Graph


class BaseLayer(ABC):
    @property
    @abstractmethod
    def variables(self):
        pass
    
    
class DataLayer(BaseLayer):
    @abstractmethod    
    def make_generator_training(self):
        pass

    @abstractmethod    
    def make_generator_validation(self):
        pass

    @abstractmethod    
    def make_generator_testing(self):
        pass

    @property
    @abstractmethod        
    def sample(self):
        pass

    @property
    @abstractmethod
    def size_training(self):
        pass

    @property
    @abstractmethod
    def size_validation(self):
        pass

    @property
    @abstractmethod
    def size_testing(self):
        pass


class InnerLayer(BaseLayer):
    @abstractmethod
    def __call__(self, x: ...):
        pass

    
class Tf1xLayer(InnerLayer):
    @property
    @abstractmethod
    def trainable_variables(self):
        pass

    @overload
    @abstractmethod
    def __call__(self, x: tf.Tensor):
        pass

    @overload
    @abstractmethod
    def __call__(self, x: List[tf.Tensor]):
        pass
    
    
class Tf2xLayer(InnerLayer):
    @abstractmethod
    def get_trainable_variables(self):
        pass

    
class TrainingLayer(DataLayer):
    #def run(self, graph: Graph):
    #    pass

    @abstractmethod
    def on_pause(self):
        pass

    @property
    @abstractmethod
    def status(self):
        raise NotImplementedError
    

class Tf1xClassificationLayer(TrainingLayer):
    @property
    @abstractmethod
    def accuracy_training(self):
        pass

    @property
    @abstractmethod
    def accuracy_validation(self):
        pass

    @property
    @abstractmethod
    def accuracy_testing(self):
        pass
    
    @property
    @abstractmethod
    def loss_training(self):
        pass

    @property
    @abstractmethod
    def loss_validation(self):
        pass

    @property
    @abstractmethod
    def loss_testing(self):
        pass

    @property
    @abstractmethod    
    def layer_gradients(self):
        pass

    @property
    @abstractmethod    
    def layer_weights(self):
        pass

    @property
    @abstractmethod    
    def layer_outputs(self):
        pass
    
