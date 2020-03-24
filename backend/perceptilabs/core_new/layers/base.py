""" Contains classes that serve as interfaces for code generated from templates. 

ALL variables needed by the frontend should be represented in these classes. 
"""

#from perceptilabs.core_new.graph import Graph

import numpy as np
import tensorflow as tf
from abc import ABC, abstractmethod
from typing import Dict, Any, overload, List, Generator

from perceptilabs.core_new.utils import Picklable


class BaseLayer(ABC):
    """Base class for any PerceptiLabs graph layer"""
    @property
    @abstractmethod
    def variables(self) -> Dict[str, Picklable]:
        """Any variables belonging to this layer that should be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and picklable for values.
        """
        raise NotImplementedError
    
    
class DataLayer(BaseLayer):
    """ Base class for loading data. The data is accessed via the generators, one sample at a time, in a fixed sequence. ̈́
    Therefore, it is left up to the consuming layers (usually a training layer) to perform any shuffling. 
    """
    
    @abstractmethod    
    def make_generator_training(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of training data."""
        raise NotImplementedError

    @abstractmethod    
    def make_generator_validation(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of validation data."""        
        raise NotImplementedError

    @abstractmethod    
    def make_generator_testing(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of testing data."""        
        raise NotImplementedError

    @property
    @abstractmethod        
    def sample(self) -> np.ndarray:
        """Returns a single data sample"""
        raise NotImplementedError

    @property
    @abstractmethod
    def size_training(self) -> int:
        """Returns the size of the training dataset"""                            
        raise NotImplementedError

    @property
    @abstractmethod
    def size_validation(self) -> int:
        """Returns the size of the validation dataset"""                                    
        raise NotImplementedError

    @property
    @abstractmethod
    def size_testing(self) -> int:
        """Returns the size of the testing dataset"""                                            
        raise NotImplementedError


class InnerLayer(BaseLayer):
    """Base class for any layer that is not a DataLayer or TrainingLayer. These layers typically transform the data somehow."""
    
    @abstractmethod
    def __call__(self, x: ...) -> Any:
        """ Returns a transformed version of the input data.

        Args:
            x: some form of input (e.g., a tf.Tensor).

        Returns:
            The transformed input data.
        """
        raise NotImplementedError

    
class Tf1xLayer(InnerLayer):
    """Wrapper for TensorFlow 1.x layers. These layers take tf.Tensor(s) as input and return a new tf.Tensor."""
    @property
    @abstractmethod
    def trainable_variables(self) -> Dict[str, tf.Tensor]:
        """Any trainable variables belonging to this layer that should be updated during backpropagation. Their gradients will also be rendered in the frontend.
        
        Returns:
            A dictionary with tensor names for keys and tensors for values.
        """
        raise NotImplementedError

    @overload
    @abstractmethod
    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        """ Returns a transformed version of the input tensor.

        Args:
            x: a tf.Tensor.

        Returns:
            The transformed input data as a tf.Tensor.
        """
        raise NotImplementedError

    @overload
    @abstractmethod
    def __call__(self, x: List[tf.Tensor]) -> tf.Tensor:
        """ Returns a transformed version of the input tensors.

        Args:
            x: a list of tf.Tensors.

        Returns:
            The transformed input data as a tf.Tensor.
        """
        
        raise NotImplementedError

    @property
    @abstractmethod
    def weights(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        raise NotImplementedError
    
    @property
    @abstractmethod
    def biases(self) -> Dict[str, tf.Tensor]:
        """Any weight tensors belonging to this layer that should be rendered in the frontend.

        Return:
            A dictionary with tensor names for keys and tensors for values.
        """        
        raise NotImplementedError
        
    
class TrainingLayer(DataLayer):
    """Base class for training layers. When run, a training layer will receive a PerceptiLabs 'Graph' object as input. 
    It is up to the implementation to execute all the contents of the graph and returning the values.

    Training layers are also data layers. This enables chaining of several subgraphs, where the training layers are run in sequence. 
    A later training layer would treat an earlier training layer as a data layer. 
    """
    
    #@property
    #@abstractmethod
    #def run(self, graph: Graph):
    #    raise NotImplementedError

    @abstractmethod
    def on_stop(self) -> None:
        """Called when the stop button is clicked in the frontend. 
        It is up to the implementing layer to save the model to disk.
        """
        raise NotImplementedError
    
    @abstractmethod
    def on_export(self, path: str, mode: str) -> None:
        """Called when the export model button is clicked in the frontend. 
        It is up to the implementing layer to export the model to disk.
        
        Args:
            path: the path to a directory where the model will be stored.
            mode: how to export the model. Made available to frontend via 'export_modes' property."""
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self):
        """Called when the pause button is clicked in the frontend. It is up to the implementing layer to pause its execution.
        """        
        raise NotImplementedError
    
    @property
    @abstractmethod    
    def progress(self) -> float:
        """A number indicating the overall progress of the training
        
        Returns:
            A floating point number between 0 and 1
        """
        raise NotImplementedError

    @property
    @abstractmethod    
    def layer_outputs(self) -> Dict[str, Dict[str, Picklable]]:
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs. The values must be picklable.
        """
        raise NotImplementedError

    @property
    def export_modes(self) -> List[str]:
        """Returns the possible modes of exporting a model."""
        raise NotImplementedError
    

class ClassificationLayer(TrainingLayer):
    """A layer for training classifiers."""
    
    @property
    @abstractmethod
    def accuracy_training(self) -> float:
        """Returns the current accuracy of the training phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def accuracy_validation(self) -> float:
        """Returns the current accuracy of the validation phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def accuracy_testing(self) -> float:
        """Returns the current accuracy of the testing phase"""                
        raise NotImplementedError
    
    @property
    @abstractmethod
    def loss_training(self) -> float:
        """Returns the current loss of the training phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_validation(self) -> float:
        """Returns the current loss of the validation phase"""                
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_testing(self) -> float:
        """Returns the current loss of the testing phase"""                        
        raise NotImplementedError

    @property
    @abstractmethod    
    def layer_weights(self) -> Dict[str, Dict[str, Picklable]]:
        """The weight values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. The values must be picklable.
        """        
        raise NotImplementedError

    @property
    @abstractmethod    
    def layer_biases(self) -> Dict[str, Dict[str, Picklable]]:
        """The bias values of each layer in the input Graph during the training.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain weight name and value pairs. The values must be picklable.
        """        
        raise NotImplementedError
    
    @property
    @abstractmethod    
    def layer_gradients(self) -> Dict[str, Dict[str, Picklable]]:
        """The gradients with respect to the loss of all trainable variables of each layer in the input Graph.

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain gradient name and value pairs. The values must be picklable.
        """        
        raise NotImplementedError
    
    @property
    @abstractmethod    
    def batch_size(self) -> int:
        """Size of the current training batch """
        raise NotImplementedError

    @property
    @abstractmethod
    def epoch(self) -> int:
        """The current epoch"""
        raise NotImplementedError
    
    @property
    def training_iteration(self) -> int:
        """The current training iteration"""
        return self._training_iteration

    @property
    def validation_iteration(self) -> int:
        """The current validation iteration"""        
        return self._validation_iteration

    @property
    def testing_iteration(self) -> int:
        """The current testing iteration"""                
        return self._testing_iteration
