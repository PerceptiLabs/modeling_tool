""" Contains classes that serve as interfaces for code generated from templates. 

ALL variables needed by the frontend should be represented in these classes. 
"""

#from perceptilabs.core_new.graph import Graph

import numpy as np
import tensorflow as tf
from abc import ABC, abstractmethod
from typing import Dict, Any, overload, List, Generator

from perceptilabs.core_new.utils import Picklable
import perceptilabs.utils as utils

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
    """ Base class for any data layer. Different data layers required are built using DataLayer as the base class. Edit this description"""
    @property
    @abstractmethod        
    def sample(self) -> np.ndarray:
        """Returns a single data sample"""
        raise NotImplementedError

class DataSupervised(DataLayer):
    """ Base class for loading data for supervised models. The data is accessed via the generators, one sample at a time, in a fixed sequence. ̈́
    Therefore, it is left up to the consuming layers (usually a training layer) to perform any shuffling. 
    """

    @property
    @abstractmethod
    def columns(self) -> List[str]: 
        """Column names. Corresponds to each column in a sample """
        raise NotImplementedError
    
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

class DataRandom(DataSupervised):
    """ Base class for generating random data for algorithms like GAN. The data is accessed via the generators, one sample at a time, in a fixed sequence."""

    pass

class DataReinforce(DataLayer):
    """ Base class for loading enviroments for Reinforcement Learning. The data is accessed via the generator, one step at a time. """

    @abstractmethod    
    def make_generator(self) -> Generator[np.ndarray, None, None]:
        """Returns a generator yielding single samples of data."""
        raise NotImplementedError

    @abstractmethod
    def reset_environment(self, generator):
        """ Resets the current environment. """
        raise NotImplementedError

    @property
    @abstractmethod
    def action_space(self) -> int:
        """ Returns the action space of the environment. """
        raise NotImplementedError

    @abstractmethod
    def take_action(self, generator, action):
        """ Takes the generator and the action as inputs and returns the new state info of the environment after taking the action."""
        raise NotImplementedError

class InnerLayer(BaseLayer):
    """Base class for any layer that is not a DataLayer or Training Layer. These layers typically transform the data somehow."""
    @abstractmethod
    def __call__(self, x) -> Any:
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
    def __call__(self, inputs: Dict[str, tf.Tensor]) -> Dict[str, tf.Tensor]:
        """ Returns a transformed version of the input tensor.

        Args:
            x: a tf.Tensor.

        Returns:
            The transformed input data as a tf.Tensor.
        """
        raise NotImplementedError

    @abstractmethod
    def get_sample(self) -> Dict[str, tf.Tensor]:
        """ Returns a dictionary of sample tensors

        Returns:
            A dictionary of sample tensors
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


class Tf2xLayer(Tf1xLayer):
    """ This layer is an adapter between Keras layers and our infrastructure for sending data.
    
    NOTE: The properties of this layer likely have to be updated as new TF2 layers are added. For example, make sure all weights are returned with the correct name. 
    """

    def __init__(self, keras_class):
        self._keras_class = keras_class
        self._keras_layer = None
        self._outputs = {'output': None}

    @property
    def keras_layer(self):
        if self._keras_layer is None:
            self._keras_layer = self._keras_class()
        return self._keras_layer
    
    def __call__(self, *args, **kwargs):        
        self._outputs = self.keras_layer(*args, **kwargs)
        return self._outputs

    def get_sample(self):
        vars_ = self._outputs.copy()
        if 'preview' in vars_:
            vars_['output'] = vars_['preview'] # Overwrite the output with the preview variable. 
        else:
            raise RuntimeError(
                "Could not fetch 'preview' variable from Keras layer. "
                "This variable must be declared as an output in order for "
                "the previews to work properly."
            )
        return vars_

    @property
    def variables(self):
        return self.keras_layer.get_config()

    @property
    def trainable_variables(self):
        dict_ = {}
        dict_.update(self.weights)
        dict_.update(self.biases)
        return dict_

    @property
    def weights(self):
        """ Return the trainable weight of a layer """        
        if hasattr(self.keras_layer, 'kernel') and self.keras_layer.kernel.trainable:
            return {'W': self.keras_layer.kernel}
        elif hasattr(self.keras_layer, 'conv') and self.keras_layer.conv.kernel.trainable:
            return {'W': self.keras_layer.conv.kernel}            
        else:
            return {}
        
    @property
    def biases(self):
        """ Return the trainable bias of a layer """
        if hasattr(self.keras_layer, 'bias') and self.keras_layer.bias.trainable:        
            return {'b': self.keras_layer.bias}
        elif hasattr(self.keras_layer, 'conv') and self.keras_layer.conv.bias.trainable:
            return {'b': self.keras_layer.conv.bias}            
        else:
            return {}

        
class TrainingLayer(DataLayer):
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

class TrainingSupervised(TrainingLayer, DataSupervised):
    """Base class for supervised training layers. When run, a training layer will receive a PerceptiLabs 'Graph' object as input. 
    It is up to the implementation to execute all the contents of the graph and returning the values.

    Training layers are also data layers. This enables chaining of several subgraphs, where the training layers are run in sequence. 
    A later training layer would treat an earlier training layer as a data layer. 
    """
    #@property
    #@abstractmethod
    #def run(self, graph: Graph):
    #    raise NotImplementedError

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def columns(self) -> List[str]: 
        """Column names. Corresponds to each column in a sample """
        raise NotImplementedError
    
class TrainingRandom(TrainingLayer, DataRandom):
    """Base class for training layers that depend on mainly Random Data component like GAN for example. When run, a training layer will receive a PerceptiLabs 'Graph' object as input. 
    It is up to the implementation to execute all the contents of the graph and returning the values.

    Training layers are also data layers. This enables chaining of several subgraphs, where the training layers are run in sequence. 
    A later training layer would treat an earlier training layer as a data layer. 
    """
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def columns(self) -> List[str]: 
        """Column names. Corresponds to each column in a sample """
        raise NotImplementedError

class TrainingReinforce(TrainingLayer, DataReinforce):
    """Base class for Reinforcement learning training layers. When run, a training layer will receive a PerceptiLabs 'Graph' object as input. 
    It is up to the implementation to execute all the contents of the graph and returning the values.

    Training layers are also data layers. This enables chaining of several subgraphs, where the training layers are run in sequence. 
    A later training layer would treat an earlier training layer as a data layer. 
    """
    def __init__(self):
        super().__init__()
    
class RegressionLayer(TrainingSupervised):
    """A layer for training regression models."""
    # @property
    # @abstractmethod
    # def columns(self) -> List[str]: 
    #     """Column names. Corresponds to each column in a sample """
    #     raise NotImplementedError

    @property
    @abstractmethod
    def loss_training(self) -> float:
        """Returns the current correctness of the training phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_validation(self) -> float:
        """Returns the current correctness of the validation phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_testing(self) -> float:
        """Returns the current correctness of the testing phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def squared_error_training(self) -> float:
        """Returns the current squared error of the training phase"""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def squared_error_testing(self) -> float:
        """Returns the current squared error of the testing phase"""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def squared_error_validation(self) -> float:
        """Returns the current squared error of the validation phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def squared_variance_training(self) -> float:
        """Returns the squared variance of the training phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def squared_variance_testing(self) -> float:
        """Returns the squared variance of the testing phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def squared_variance_validation(self) -> float:
        """Returns the squared variance of the validation phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def batch_size(self) -> float:
        """Returns the batch size"""
        raise NotImplementedError

    @property
    @abstractmethod
    def r_squared_training(self) -> float:
        """Returns the R^2 of the training phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def r_squared_testing(self) -> float:
        """Returns the R^2 of the testing phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def r_squared_validation(self) -> float:
        """Returns the R^2 of the validation phase"""
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
    @abstractmethod
    def training_iteration(self) -> int:
        """The current training iteration"""
        return self._training_iteration

    @property
    @abstractmethod
    def validation_iteration(self) -> int:
        """The current validation iteration"""        
        return self._validation_iteration

    @property
    @abstractmethod
    def testing_iteration(self) -> int:
        """The current testing iteration"""                
        return self._testing_iteration
    
class ClassificationLayer(TrainingSupervised):
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
    def auc_training(self) -> float:
        """Returns the current AUC score of the training phase"""

        if utils.is_tf2x():
            raise NotImplementedError
        else:
            return -1.0
            
    @property
    def auc_validation(self) -> float:
        """Returns the current AUC score of the validation phase"""
        if utils.is_tf2x():
            raise NotImplementedError
        else:
            return -1.0
    
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

class ObjectDetectionLayer(TrainingSupervised):
    """A layer for training classifiers."""
    
    @property
    @abstractmethod
    def accuracy_training(self) -> float:
        """Returns the current classification accuracy of the training phase"""
        raise NotImplementedError

    @property
    @abstractmethod
    def accuracy_validation(self) -> float:
        """Returns the current classification accuracy of the validation phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def accuracy_testing(self) -> float:
        """Returns the current classification accuracy of the testing phase"""                
        raise NotImplementedError
    
    @property
    def image_accuracy(self) -> float:
        return self._image_accuracy

    @property
    @abstractmethod
    def loss_bbox_training(self) -> float:
        """Returns the current loss of the training phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_bbox_validation(self) -> float:
        """Returns the current loss of the validation phase"""                
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_bbox_testing(self) -> float:
        """Returns the current loss of the testing phase"""                        
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_classification_training(self) -> float:
        """Returns the current loss of the training phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_classification_validation(self) -> float:
        """Returns the current loss of the validation phase"""                
        raise NotImplementedError

    @property
    @abstractmethod
    def loss_classification_testing(self) -> float:
        """Returns the current loss of the testing phase"""                        
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
    @abstractmethod
    def grid_size(self) -> int:
        """ size of the grid """
        return self._grid_size
    
    @property
    def classes(self) -> List[str]:
        """classes in the dataset"""
        return self._classes

    @property
    @abstractmethod
    def num_class(self) -> int:
        """ number of classes in the dataset"""
        return self._num_class

    @property 
    @abstractmethod  
    def num_box(self) -> int:
        """ number of boxes per grid"""
        return self._num_box 

    @property
    @abstractmethod
    def lambdaclass(self) -> float:
        return self._lambdaclass
        
    @property
    @abstractmethod
    def lambdanoobj(self) -> float:  
        return self._lambdanoobj

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

    @property
    def get_predicted_normalized_boxes(self) -> np.ndarray:
        """ """
        return self._predicted_normalized_box

    @property
    def get_predicted_classes(self) -> np.ndarray:
        """ """
        return self._predicted_class

    @property
    def get_predicted_objects(self) -> np.ndarray:
        """ """
        return self._predicted_object


    @property
    def get_input_data_node(self):
        """ node corresponding to input tensor"""
        return self._input_data_node

class RLLayer(TrainingReinforce):
    
    @property
    @abstractmethod    
    def batch_size(self) -> int:
        """Size of the current training batch """
        raise NotImplementedError


    @property
    @abstractmethod
    def episode(self) -> int:
        """The current episode"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def n_episodes(self) -> int:
        """number of episodes"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def gamma(self) -> float:
        """ gamma """
        raise NotImplementedError

    @property
    @abstractmethod
    def replay_memory_size(self) -> int:
        """ replay memory size """
        raise NotImplementedError

    @property
    @abstractmethod
    def transition(self) -> Dict[str, Picklable]:
        """ replay memory """
        raise NotImplementedError

    @property
    @abstractmethod
    def n_actions(self) -> int:
        """ _n actions """
        raise NotImplementedError

    @property
    @abstractmethod
    def n_steps_max(self) -> int:
        """ _n_steps_max """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def step_counter(self) -> int:
        """  step counter """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def history_length(self) -> int:
        """ history length"""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def reward(self) -> float:
        """ returns reward during one iteration"""
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
    def layer_outputs(self) -> Dict[str, Dict[str, Picklable]]:
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)
        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs. The values must be picklable.
        """
        raise NotImplementedError

class GANLayer(TrainingRandom):
    """A layer for training GANs"""
    
    @property
    @abstractmethod
    def generator_loss_training(self) -> float:
        """Returns the current loss of the training phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def generator_loss_validation(self) -> float:
        """Returns the current loss of the validation phase"""                
        raise NotImplementedError

    @property
    @abstractmethod
    def generator_loss_testing(self) -> float:
        """Returns the current loss of the testing phase"""                        
        raise NotImplementedError

    @property
    @abstractmethod
    def discriminator_loss_training(self) -> float:
        """Returns the current loss of the training phase"""        
        raise NotImplementedError

    @property
    @abstractmethod
    def discriminator_loss_validation(self) -> float:
        """Returns the current loss of the validation phase"""                
        raise NotImplementedError

    @property
    @abstractmethod
    def discriminator_loss_testing(self) -> float:
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

    @property
    @abstractmethod   
    def generator_layer_outputs(self) -> Dict[str, Dict[str, Picklable]]:
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs. The values must be picklable.
        """
        raise NotImplementedError

    @property
    @abstractmethod   
    def real_layer_outputs(self) -> Dict[str, Dict[str, Picklable]]:
        """The output values of each layer in the input Graph during the training (e.g., tf.Tensors evaluated for each iteration)

        Returns:
            A dictionary of nested dictionaries, where each key is a layer id. The nested dictionaries contain variable name and value pairs. The values must be picklable.
        """
        raise NotImplementedError

    @property 
    @abstractmethod  
    def get_switch_layer_id(self) -> str:
        return self._switch_layer_id
    
