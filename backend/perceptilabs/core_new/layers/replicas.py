import tensorflow as tf
from typing import List, Callable



from perceptilabs.core_new.layers import DataLayer, TrainingLayer, Tf1xLayer, ClassificationLayer, InnerLayer, ObjectDetectionLayer


class NotReplicatedError(Exception):
    pass


class DataLayerReplica(DataLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables, columns):
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation
        self._size_testing = size_testing
        self._variables = variables
        self._columns = columns        

    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
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
    
    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    
class ClassificationLayerReplica(ClassificationLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation,
                 loss_training, loss_testing, loss_validation,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, export_modes, columns):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._columns = columns        
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._accuracy_training = accuracy_training 
        self._accuracy_validation = accuracy_validation
        self._accuracy_testing = accuracy_testing
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._status = status

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
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
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes




class ObjectDetectionLayerReplica(ObjectDetectionLayer):
    def __init__(self, sample, size_training, size_validation, size_testing, variables,
                 accuracy_training, accuracy_testing, accuracy_validation, image_accuracy,
                 loss_training, loss_testing, loss_validation, loss_classification_training, 
                 loss_classification_validation, loss_classification_testing, 
                 loss_bbox_training, loss_bbox_validation, loss_bbox_testing, 
                 grid_size, classes, num_box, num_class, lambdacoord, lambdanoobj,
                 get_predicted_normalized_boxes, get_predicted_classes, get_predicted_objects,
                 status, layer_weights, layer_biases, layer_gradients, layer_outputs,
                 batch_size, training_iteration, validation_iteration,
                 testing_iteration, progress, epoch, export_modes, get_input_data_node, columns):

        self._export_modes = export_modes
        self._epoch = epoch
        self._sample = sample
        self._size_training = size_training
        self._size_validation = size_validation        
        self._size_testing = size_testing
        self._variables = variables
        self._accuracy_training = accuracy_training 
        self._accuracy_validation = accuracy_validation
        self._accuracy_testing = accuracy_testing
        self._image_accuracy = image_accuracy
        self._loss_training = loss_training
        self._loss_validation = loss_validation
        self._loss_testing = loss_testing
        self._classification_loss_training = loss_classification_training
        self._classification_loss_validation = loss_classification_validation
        self._classification_loss_testing = loss_classification_testing
        self._bbox_loss_training = loss_bbox_training
        self._bbox_loss_validation = loss_bbox_validation
        self._bbox_loss_testing = loss_bbox_testing
        self._status = status

        self._grid_size = grid_size
        self._classes = classes
        self._num_box = num_box 
        self._num_class = num_class
        self._lambdacoord = lambdacoord
        self._lambdanoobj = lambdanoobj

        self._input_data_node = get_input_data_node

        self._predicted_normalized_box = get_predicted_normalized_boxes
        self._predicted_class = get_predicted_classes
        self._predicted_object = get_predicted_objects

        self._layer_weights = layer_weights
        self._layer_biases = layer_biases
        self._layer_gradients = layer_gradients
        self._layer_outputs = layer_outputs

        self._batch_size = batch_size
        self._training_iteration = training_iteration
        self._validation_iteration = validation_iteration
        self._testing_iteration = testing_iteration
        self._progress = progress
        self._columns = columns

    @property
    def epoch(self):
        return self._epoch
    
    @property
    def batch_size(self):
        return self._batch_size
    
    @property
    def grid_size(self) -> int:
        return self._grid_size
    
    @property
    def classes(self) -> List[str]:
        return self._classes

    @property
    def num_class(self) -> int:
        return self._num_class

    @property 
    def num_box(self) -> int:
        return self._num_box 

    @property
    def lambdacoord(self) -> float:
        return self._lambdacoord
        
    @property
    def lambdanoobj(self) -> float:  
        return self._lambdanoobj

    @property
    def sample(self):
        return self._sample 

    @property
    def columns(self):
        return self._columns
    
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
    def accuracy_testing(self) :
        return self._accuracy_testing

    @property
    def accuracy_validation(self):
        return self._accuracy_validation

    @property
    def image_accuracy(self) -> float:
        return self._image_accuracy

    @property
    def loss_classification_training(self) -> float:
        return self._classification_loss_training        

    @property
    def loss_classification_validation(self) -> float:
        return self._classification_loss_validation        

    @property
    def loss_classification_testing(self) -> float:
        return self._classification_loss_testing

    @property
    def loss_bbox_training(self) -> float:
        return self._bbox_loss_training        

    @property
    def loss_bbox_validation(self) -> float:
        return self._bbox_loss_validation        

    @property
    def loss_bbox_testing(self) -> float:
        return self._bbox_loss_testing

    @property
    def loss_training(self):
        return self._loss_training

    @property
    def get_predicted_normalized_boxes(self):
        return self._predicted_normalized_box

    @property
    def get_predicted_classes(self):
        return self._predicted_class

    @property
    def get_predicted_objects(self):
        return self._predicted_object

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
    def layer_biases(self):
        return self._layer_biases
    
    @property
    def layer_gradients(self):
        return self._layer_gradients

    @property
    def layer_outputs(self):
        return self._layer_outputs

    def make_generator_training(self):
        raise NotReplicatedError

    def make_generator_validation(self):
        raise NotReplicatedError        

    def make_generator_testing(self):
        raise NotReplicatedError

    def on_stop(self):
        raise NotReplicatedError        
    
    def on_export(self, path):
        raise NotReplicatedError
    
    @property
    def training_iteration(self):
        return self._training_iteration

    @property
    def validation_iteration(self):
        return self._validation_iteration

    @property
    def testing_iteration(self):
        return self._testing_iteration

    @property
    def progress(self):
        return self._progress

    @property
    def export_modes(self):
        return self._export_modes
    
    @property
    def get_input_data_node(self):
        return self._input_data_node

    


class InnerLayerReplica(InnerLayer):
    def __init__(self, variables):
        self._variables = variables

    @property        
    def variables(self):
        return self._variables

    def __call__(self, x: ...):
        raise NotReplicatedError        
    
    
class Tf1xLayerReplica(Tf1xLayer):
    def __init__(self, variables):
        self._variables = variables

    @property        
    def variables(self):
        return self._variables

    @property        
    def trainable_variables(self):
        raise NotReplicatedError        

    @property        
    def weights(self):
        raise NotReplicatedError        
    
    @property        
    def biases(self):
        raise NotReplicatedError        
    
    def __call__(self, x: tf.Tensor):
        raise NotReplicatedError        

    def __call__(self, x: List[tf.Tensor]):
        raise NotReplicatedError
