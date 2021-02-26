import collections
import time
import logging

import tensorflow as tf
import numpy as np
import time
import logging
from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER

from perceptilabs.layers.visualizer import PerceptiLabsVisualizer
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.trainer.stats import SampleStatsTracker, SampleStats, GradientStatsTracker, GradientStats
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)

class Trainer:
    def __init__(self, script_factory, data_loader, graph_spec):
        self._script_factory = script_factory
        self._data_loader = data_loader
        self._graph_spec = graph_spec
        self._training_time = 0.0
        
        self._headless = False

        self._num_epochs_completed = 0        
        self._num_epochs = 100 # TODO: read from spec (story 1535)
        self._batch_size = 2 # TODO: read from spec (story 1535)

        self._reset_tracked_values()
        self._initialize_batch_counters(data_loader)
        self._set_status('Waiting')
        
        
    def run(self, _=None, on_iterate=None, model_id=None):
        """ Run all training steps """
        # TODO: remove _, on_iterate and model_id when possible
        for _ in self.run_stepwise():
            pass
    
    def run_stepwise(self):
        """ Take a training/validation step and yield """
        logger.info("Initializing training")        

        self._training_model = TrainingModel(self._script_factory, self._graph_spec)
        logger.info("Training model initialized")
        
        dataset_train = self._data_loader.get_dataset().batch(self.batch_size)
        logger.info("Dataset loaded")
        
        self._metric_training_loss = tf.keras.metrics.Mean()
        self._metric_training_accuracy = tf.keras.metrics.CategoricalAccuracy()
        self._metric_training_auc = tf.keras.metrics.AUC(curve='ROC')
        
        self._metric_validation_loss = tf.keras.metrics.Mean()
        self._metric_validation_accuracy = tf.keras.metrics.CategoricalAccuracy()
        self._metric_validation_auc = tf.keras.metrics.AUC(curve='ROC')

        # TODO: Implement different optimizers (story 1535)
        optimizer = tf.keras.optimizers.SGD(learning_rate=0.01) #  TODO: fix learning rate (story 1535)

        losses = {
            layer_spec.feature_name: tf.keras.losses.MeanSquaredError() # TODO: get from training settings/output layers (story 1536)
            for layer_spec in self._graph_spec.layers
            if layer_spec.is_output_layer
        }

        logger.info("Entering training loop")        
        self._num_epochs_completed = 0
        while self._num_epochs_completed < self.num_epochs and not self.is_closed:
            t0 = time.perf_counter()
            self._set_status('Training')

            yield from self._loop_over_dataset(
                self._training_model,
                losses,
                dataset_train,
                self._metric_training_loss,
                self._metric_training_accuracy,
                self._metric_training_auc,
                self._set_num_training_batches_completed_this_epoch,
                training=True,
                optimizer=optimizer
            )

            time_paused_training = self._sleep_while_paused()
            if self.is_closed:
                break
            self._set_status('Validation')

            yield # TODO: loop over dataset for validation (story 1537)

            time_paused_validation = self._sleep_while_paused()
            if self.is_closed:
                break
            self._num_epochs_completed += 1
            epoch_time = time.perf_counter() - t0 - time_paused_training - time_paused_validation

            logger.info(
                f"Finished epoch {self._num_epochs_completed}/{self.num_epochs} - "
            )
            logger.info(f"Epoch duration: {round(epoch_time, 3)} s")
            self._training_time += epoch_time

            yield
            
        self._set_status('Finished')
        logger.info(f"Training completed. Total duration: {round(self._training_time, 3)} s")
        
        # TODO: automatic export at end of training (story 1538)

    def _loop_over_dataset(self, model, losses, dataset, metric_loss, metric_accuracy, metric_auc, set_num_batches_completed_this_epoch, training=True, optimizer=None):
        """ Loop over all batches of data once """
        metric_loss.reset_states()
        metric_accuracy.reset_states()
        metric_auc.reset_states()

        for step, (inputs_batch, targets_batch) in enumerate(dataset):
            predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer = self._work_on_batch(
                model, losses, inputs_batch, targets_batch, metric_loss, training, optimizer
            )
            
            if self._headless:
                self._reset_tracked_values()
            else:
                self._update_tracked_values(trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer, inputs_batch, predictions_batch, targets_batch)
            
            self._num_batches_completed_all_epochs += 1
            set_num_batches_completed_this_epoch(step + 1)            
            yield

    #@tf.function
    def _work_on_batch(self, model, losses, inputs_batch, targets_batch, metric_loss, training, optimizer):
        """ Train or validate on a batch of data """
        with tf.GradientTape() as tape:
            predictions_batch, final_and_intermediate_outputs = model(inputs_batch, training=training)
            total_loss = self._compute_total_loss(predictions_batch, targets_batch, losses)
            
        metric_loss.update_state(total_loss)
        # TODO: implement accuracy metric (story 1540)
        # TODO: implement auc metric (story 1541)

        trainables_by_layer = self._collect_trainables_by_layer(model)
        gradients_by_layer, grads_and_vars = self._compute_gradients(tape, total_loss, trainables_by_layer, model.trainable_variables)
        
        if training:
            optimizer.apply_gradients(grads_and_vars)

        return predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs

    def _compute_gradients(self, tape, total_loss, trainables_by_layer, flat_trainables):
        """ Compute the gradients. Return two variations, one structured by layer and one flat """
        gradients_by_layer, flat_gradients = tape.gradient(total_loss, (trainables_by_layer, flat_trainables))
        grads_and_vars = zip(flat_gradients, flat_trainables)
        return gradients_by_layer, grads_and_vars    

    def _compute_total_loss(self, predictions_batch, targets_batch, losses):
        """ Compute the combined loss of all output layers """
        total_loss = tf.constant(0.0)
        for output_name, loss_fn in losses.items():
            # TODO: weight the different losses (story 1542)
            total_loss += loss_fn(
                predictions_batch[output_name],
                tf.reshape(targets_batch[output_name], shape=predictions_batch[output_name].shape)
            )
        return total_loss

    def _reset_tracked_values(self):
        self._layer_outputs = {}
        self._layer_trainables = {}
        self._input_stats_tracker = SampleStatsTracker()
        self._prediction_stats_tracker = SampleStatsTracker()                        
        self._target_stats_tracker = SampleStatsTracker()
        self._gradient_stats_tracker = GradientStatsTracker()

    def _update_tracked_values(self, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer, inputs_batch, predictions_batch, targets_batch):
        """ Take a snapshot of the current tensors (e.g., layer weights) """
        self._layer_outputs = final_and_intermediate_outputs_by_layer
        self._layer_trainables = trainables_by_layer
        
        self._input_stats_tracker.update(graph_spec=self._graph_spec, sample_batch=inputs_batch)
        self._prediction_stats_tracker.update(graph_spec=self._graph_spec, sample_batch=predictions_batch)                
        self._target_stats_tracker.update(graph_spec=self._graph_spec, sample_batch=targets_batch)
        self._gradient_stats_tracker.update(gradients_by_layer=gradients_by_layer)

    def _collect_trainables_by_layer(self, model):
        """ Collect the trainable tensors from the model and structure them by layer """
        trainables_by_layer = {}
        for layer_id, layer in model.layers_by_id.items():
            if isinstance(layer, PerceptiLabsVisualizer):
                weights, bias = layer.visualized_trainables
                
                trainables = {}
                if isinstance(weights, tf.Variable):
                    trainables['weights'] = weights
                if isinstance(bias, tf.Variable):
                    trainables['bias'] = bias
                    
                if trainables:
                    trainables_by_layer[layer_id] = trainables
                
            elif len(layer.trainable_variables) > 0:
                logger.warning("Layer {layer_id} has trainable variables but does not implement the PerceptiLabsVisualizer abstract class. Weights, biases and derived quantities such as gradients will not be visualized correctly.")
                
        return trainables_by_layer

    def _set_num_training_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """
        self._num_training_batches_completed_this_epoch = value

    def _set_num_validation_batches_completed_this_epoch(self, value):
        """ The number of iterations completed in the _current_ epoch """        
        self._num_validation_batches_completed_this_epoch = value

    def _set_status(self, value):
        if value not in ['Waiting', 'Paused', 'Training', 'Validation', 'Finished']:
            raise ValueError(f"Cannot set status to '{value}'")
        self._status = value

    @property
    def status(self):
        """ The current training status """
        return self._status
        
    @property
    def batch_size(self):
        return self._batch_size

    @property
    def num_epochs(self):
        return self._num_epochs

    @property
    def num_epochs_completed(self):
        return self._num_epochs_completed

    @property
    def num_batches_completed_all_epochs(self):
        return self._num_batches_completed_all_epochs

    @property
    def num_batches_all_epochs(self):
        return self._num_batches_all_epochs

    @property
    def num_batches_per_epoch(self):
        return self._num_batches_per_epoch

    @property
    def num_batches_completed_this_epoch(self):
        return self.num_training_batches_completed_this_epoch + self.num_validation_batches_completed_this_epoch
    @property
    def num_training_batches_completed_this_epoch(self):
        return self._num_training_batches_completed_this_epoch

    @property
    def num_validation_batches_completed_this_epoch(self):
        return self._num_validation_batches_completed_this_epoch

    def _initialize_batch_counters(self, data_loader):
        """ Initialize iteration/batch counters to keep track of progress """
        dataset_size = len(list(data_loader.get_dataset()))

        self._num_batches_per_epoch = int(np.ceil(dataset_size / self.batch_size))
        self._num_batches_all_epochs = self._num_batches_per_epoch * self._num_epochs
        self._num_batches_completed_all_epochs = 0

        self._set_num_training_batches_completed_this_epoch(0)
        self._set_num_validation_batches_completed_this_epoch(0)

    @property
    def progress(self) -> float:
        return self.num_batches_completed_all_epochs / self.num_batches_all_epochs

    @property
    def is_closed(self):
        return self.status == 'Finished'

    @property
    def is_ready(self):
        return True

    @property
    def is_paused(self):
        return self.status == 'Paused'
    
    def _sleep_while_paused(self):
        t0 = time.perf_counter()
        while self.is_paused:
            time.sleep(1)

        return time.perf_counter() - t0

    def _store_prev_status(self):
        if self.status == 'Training':
            self._prev_status = 'Training'
        if self.status == 'Validation':
            self._prev_status = 'Validation'
        
    def pause(self):
        self._store_prev_status()
        self._set_status('Paused')
        logger.info(f"Trainer is in state Paused")
        
    def unpause(self):
        self._set_status(self._prev_status)
        logger.info(f"Trainer is in state %s", self._prev_status)

    def stop(self):
        self._set_status('Finished')
    
    def headless_on(self):
        # TODO: implement (story 1545)
        pass
    
    def headless_off(self):
        # TODO: implement (story 1545)
        pass        

    def export(self, path, mode):
        # TODO: implement (1538)
        if mode == 'TFModel':
            self.save_model(path)

    def close(self):
        self.stop()
        
    def save_model(self, path):
        """ Save the model """
        model = self.get_inference_model()
        model.save(path)

    def get_inference_model(self):
        """ Convert the Training Model to a simpler version (e.g., skip intermediate outputs)  """        
        # TODO: add option to include pre- and post-processing pipelines (story 1609)
        inputs = {}
        for layer_spec in self._graph_spec:
            if not layer_spec.is_input_layer:
                continue
            shape = self._data_loader.get_feature_shape(layer_spec.feature_name)
            inputs[layer_spec.feature_name] = tf.keras.Input(shape=shape)
                
        outputs, _ = self._training_model(inputs)
        inference_model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return inference_model        

    def get_layer_output(self, layer_id, output_variable='output'):
        """ Gets the output batch of a layer 
        
        Arguments:
            layer_id: the layer id
            output_variable: which variable to fetch from the output dict
        Returns:
            A numpy array (or None if the layer/variable doesnt exist)            
        """
        try:
            output_batch = self._layer_outputs[layer_id][output_variable].numpy()
            return output_batch
        except KeyError as e:
            return None

    def get_layer_weights(self, layer_id):
        """ Get the weights associated with a layer """
        try:
            value = self._layer_trainables[layer_id]['weights'].numpy()
            return value
        except KeyError as e:
            return None

    def get_layer_bias(self, layer_id):
        """ Get the bias associated with a layer """        
        try:
            value = self._layer_trainables[layer_id]['bias'].numpy()
            return value
        except KeyError as e:
            return None

    def get_target_stats(self) -> SampleStats:
        """ Returns a stats object for the current target values """
        return self._target_stats_tracker.save()
        
    def get_prediction_stats(self) -> SampleStats:
        """ Returns a stats object for the current prediction values """
        return self._prediction_stats_tracker.save()
        
    def get_input_stats(self) -> SampleStats:
        """ Returns a stats object for the current input values """
        return self._input_stats_tracker.save()

    def get_layer_gradients(self, layer_id, aggregation):
        """ Get the gradients of a layer
        
        Arguments:
            layer_id: the layer id
            aggregation: one of minimum, maximum and average
        """
        stats = self._gradient_stats_tracker.save()
        if aggregation == 'minimum':
            return stats.get_minimum_by_layer_id(layer_id)
        elif aggregation == 'average':
            return stats.get_average_by_layer_id(layer_id)            
        elif aggregation == 'maximum':
            return stats.get_maximum_by_layer_id(layer_id)                        
        
    def _get_train_dict(self):
        dict_ = {}
        for layer_spec in self._graph_spec.layers:
            # TODO: implement accuracy (story 1540)
            # TODO: implement auc metric (story 1541)
            # TODO: implement loss (story 1571)
            
            dict_[layer_spec.id_] = {
                'X': {'input1': {'Y': 123}}, # TODO: fix [this is only used in training layer] (story 1566)
                'Y': self.get_layer_output(layer_spec.id_),
                'W': self.get_layer_weights(layer_spec.id_),
                'b': self.get_layer_bias(layer_spec.id_),
                'Gradient': { 
                    'Min': self.get_layer_gradients(layer_spec.id_, 'minimum'), 
                    'Max': self.get_layer_gradients(layer_spec.id_, 'maximum'),
                    'Average': self.get_layer_gradients(layer_spec.id_, 'average')
                }
            }
        return dict_

    def get_results(self):
        """ Return a dict for the coreInterface to derive plots from """
        t0 = time.perf_counter()        
        dict_ = {
            'iter': self.num_batches_completed_this_epoch,
            'maxIter': self.num_batches_per_epoch,
            'epoch': self.num_epochs_completed,
            'maxEpochs': self.num_epochs,
            'batch_size': self.batch_size,
            'trainingIterations': self.num_training_batches_completed_this_epoch,
            'trainDict': self._get_train_dict(),
            'trainingStatus': self.status,
            'progress': self.progress, 
            'status': 'Paused' if self.is_paused else 'Running',
            'training_duration': self._training_time,
            'input_stats': self.get_input_stats(),
            'prediction_stats': self.get_prediction_stats(),
            'target_stats': self.get_target_stats()
        }
        t1 = time.perf_counter()
        logger.debug(f"get_results finished. Duration: {t1 - t0}")        
        return dict_

    def get_target_stats(self) -> SampleStats:
        """ Returns a tracker for the current target values """
        return self._target_stats_tracker.save()
