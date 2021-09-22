import collections
import os
import time
import logging
from typing import Dict

import tensorflow as tf
import numpy as np
import json
import time
import logging

from perceptilabs.logconf import APPLICATION_LOGGER, USER_LOGGER
from perceptilabs.layers.visualizer import PerceptiLabsVisualizer
from perceptilabs.trainer.model import TrainingModel
from perceptilabs.resources.epochs import EpochsAccess
from perceptilabs.stats import SampleStatsTracker, SampleStats, GradientStatsTracker, GradientStats, GlobalStatsTracker, TrainingStatsTracker
from perceptilabs.layers.iooutput.stats import ImageOutputStatsTracker, NumericalOutputStatsTracker, CategoricalOutputStatsTracker, MaskOutputStatsTracker
from perceptilabs.trainer.losses import weighted_crossentropy, dice
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.utils import get_memory_usage, sanitize_path
import perceptilabs.tracking as tracking
import perceptilabs.utils as utils
import perceptilabs.settings as settings


logger = logging.getLogger(APPLICATION_LOGGER)


class Trainer:
    def __init__(self, data_loader, training_model, training_settings, checkpoint_directory=None, exporter=None, model_id=None, user_email=None, initial_state=None):
        self._initial_state = initial_state
        self._training_settings = training_settings.copy()

        self._model_id = model_id
        self._user_email = user_email

        self._data_loader = data_loader
        self._training_model = training_model
        self._graph_spec = training_model.graph_spec
        self._exporter = exporter

        self._optimizer = self._resolve_optimizer(self._training_settings)
        self._loss_functions = self._setup_loss_functions(self._training_settings)

        self._checkpoint_directory = checkpoint_directory
        self._auto_checkpoint = training_settings.get('AutoCheckpoint', False)

        self._initialize_results()
        self._data_initialized = False

    def _initialize_results(self):
        self._num_epochs = int(self._training_settings['Epochs'])
        self._batch_size = int(self._training_settings['Batch_size'])
        self._shuffle_training_set = self._training_settings['Shuffle']
        self._headless = False

        self._num_batches_per_epoch = -1  # Not known until data loader is ran
        self._num_batches_all_epochs = -1  # Not known until data loader is ran

        if self._initial_state is None:
            self._set_status('Waiting')
            self._training_time = 0.0
            self._num_epochs_completed = 0
            self._num_batches_completed_all_epochs = 0
            self._set_num_training_batches_completed_this_epoch(0)
            self._set_num_validation_batches_completed_this_epoch(0)
        else:
            initial_state = self._initial_state
            self._set_status(self._initial_state['status'])
            self._training_time = initial_state['training_time']
            self._num_epochs_completed = initial_state['num_epochs_completed']
            self._num_batches_completed_all_epochs = initial_state['num_batches_completed_all_epochs']
            self._set_num_training_batches_completed_this_epoch(
                initial_state['num_training_batches_completed_this_epoch'])
            self._set_num_validation_batches_completed_this_epoch(
                initial_state['num_validation_batches_completed_this_epoch'])

        self._reset_tracked_values(self._initial_state)

    def ensure_data_initialized(self):
        if self._data_initialized:
            return

        self._data_loader.ensure_initialized()
        training_size = self._data_loader.get_dataset_size(partition='training')
        validation_size = self._data_loader.get_dataset_size(partition='validation')

        training_batches_per_epoch = int(np.ceil(training_size / self._batch_size))
        validation_batches_per_epoch = int(np.ceil(validation_size / self._batch_size))

        self._num_batches_per_epoch = training_batches_per_epoch + validation_batches_per_epoch
        self._num_batches_all_epochs = self._num_batches_per_epoch * self._num_epochs
        self._data_initialized = True

    def save_state(self):
        state = {
            'status': self._status,
            'training_time': self._training_time,
            'num_epochs_completed': self._num_epochs_completed,
            'num_batches_completed_all_epochs': self._num_batches_completed_all_epochs,
            'num_training_batches_completed_this_epoch': self._num_training_batches_completed_this_epoch,
            'num_validation_batches_completed_this_epoch': self._num_validation_batches_completed_this_epoch,
            'layer_outputs': self._layer_outputs,
            'layer_trainables': self._layer_trainables,
            'global_stats_tracker': self._global_stats_tracker,
            'input_stats_tracker': self._input_stats_tracker,
            'prediction_stats_tracker': self._prediction_stats_tracker,
            'target_stats_tracker': self._target_stats_tracker,
            'gradient_stats_tracker': self._gradient_stats_tracker,
            'output_trackers': {
                layer_id: tracker
                for layer_id, tracker in self._output_trackers.items()
            }
        }
        return state

    def validate(self):
        """ Compute the loss. If the model or data is faulty, we get a crash.

        Should be seen as a final error check
        """
        dataset = self._data_loader.get_dataset().batch(1)
        inputs_batch, targets_batch = next(iter(dataset))

        predictions_batch, final_and_intermediate_outputs = self._training_model(
            inputs_batch, training=False)
        self._compute_total_loss(
            predictions_batch, targets_batch, self._loss_functions)

    def run(self, _=None, on_iterate=None, model_id=None):
        """ Run all training steps """
        # TODO: remove _, on_iterate and model_id when possible
        for _ in self.run_stepwise():
            pass

    def run_stepwise(self):
        """ Take a training/validation step and yield """
        self.ensure_data_initialized()
        peak_memory_usage = get_memory_usage()

        if self._user_email:
            tracking.send_training_started(self._user_email, self._model_id, self._graph_spec)

        if self._num_epochs_completed == 0:
            logger.info("Entering training loop")
        else:
            logger.info(f"Entering training loop (starting from epoch {self._num_epochs_completed}/{self.num_epochs})")

        if self._checkpoint_directory is not None:
            logger.info(f"Checkpoints will be saved to {self._checkpoint_directory}")

        self._set_status('Training')
        while self._num_epochs_completed < self.num_epochs and not self.is_closed:
            t0 = time.perf_counter()
            self._set_status('Training')

            yield from self._loop_over_dataset(
                self._training_model,
                self._loss_functions,
                self._get_training_set(),
                self._set_num_training_batches_completed_this_epoch,
                is_training=True,
                optimizer=self._optimizer
            )
            time_paused_training = self._sleep_while_paused()
            if self.is_closed:
                break
            self._set_status('Validation')

            yield from self._loop_over_dataset(
                self._training_model,
                self._loss_functions,
                self._get_validation_set(),
                self._set_num_validation_batches_completed_this_epoch,
                is_training=False
            )

            time_paused_validation = self._sleep_while_paused()
            if self.is_closed:
                break

            if self._auto_checkpoint:
                self._auto_save_epoch(epoch=self._num_epochs_completed)

            self._num_epochs_completed += 1
            epoch_time = time.perf_counter() - t0 - time_paused_training - \
                time_paused_validation

            self._log_epoch_summary(epoch_time)
            self._training_time += epoch_time

            current_memory_usage = get_memory_usage()
            if current_memory_usage > peak_memory_usage:
                peak_memory_usage = current_memory_usage

            yield

        if not self._auto_checkpoint:  # At least save the final one.
            self._auto_save_epoch(epoch=self._num_epochs_completed)            


        self._set_status('Finished')
        logger.info(
            f"Training completed. Total duration: {round(self._training_time, 3)} s")

        if self._user_email and self._num_epochs_completed == self.num_epochs:
            tracking.send_training_completed(
                self._user_email,
                self._model_id,
                self._graph_spec,
                self._training_time,
                peak_memory_usage,
                self.get_output_stats_summaries()
            )

    def _auto_save_epoch(self, epoch):
        """ Exports the model so that we can restore it between runs """
        if self._exporter is None:
            logger.error("Exporter not set. Cannot auto export")
            return

        if self._checkpoint_directory is None:
            logger.error("Auto checkpoint dir not set. Cannot auto export")
            return

        epochs_access = EpochsAccess()
        checkpoint_path = epochs_access.get_checkpoint_path(
            training_session_id=self._checkpoint_directory,
            epoch_id=epoch
        )
        self._exporter.export_checkpoint(checkpoint_path)

        state_dict = self.save_state()
        epochs_access.save_state_dict(self._checkpoint_directory, epoch, state_dict)
        
    def _log_epoch_summary(self, epoch_time):
        logger.info(
            f"Finished epoch {self._num_epochs_completed}/{self.num_epochs} - "
            f"Epoch duration: {round(epoch_time, 3)} s - "
            f"Num training (validation) batches completed : {self.num_training_batches_completed_this_epoch} ({self.num_validation_batches_completed_this_epoch})"
        )

    def _loop_over_dataset(self, model, loss_functions, dataset, set_num_batches_completed_this_epoch, is_training=True, optimizer=None):
        """ Loop over all batches of data once """
        for steps_completed, (inputs_batch, targets_batch) in enumerate(dataset):
            predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer, \
                total_loss, individual_losses = self._work_on_batch(
                    model, loss_functions, inputs_batch, targets_batch, is_training, optimizer
                )

            if self._headless:
                self._reset_tracked_values()
            else:
                self._update_tracked_values(
                    trainables_by_layer,
                    gradients_by_layer,
                    final_and_intermediate_outputs_by_layer,
                    inputs_batch,
                    predictions_batch,
                    targets_batch,
                    total_loss,
                    individual_losses,
                    is_training,
                    steps_completed
                )

            self._num_batches_completed_all_epochs += 1
            set_num_batches_completed_this_epoch(steps_completed + 1)

            yield

    @tf.function
    def _work_on_batch(self, model, loss_functions, inputs_batch, targets_batch, is_training, optimizer):
        """ Train or validate on a batch of data """

        with tf.GradientTape() as tape:
            predictions_batch, final_and_intermediate_outputs = model(
                inputs_batch, training=is_training)
            total_loss, individual_losses = self._compute_total_loss(
                predictions_batch, targets_batch, loss_functions)

        trainables_by_layer = self._collect_trainables_by_layer(model)
        gradients_by_layer, grads_and_vars = self._compute_gradients(
            tape, total_loss, trainables_by_layer, model.trainable_variables)

        if is_training:
            optimizer.apply_gradients(grads_and_vars)

        return predictions_batch, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs, total_loss, individual_losses

    def _compute_gradients(self, tape, total_loss, trainables_by_layer, flat_trainables):
        """ Compute the gradients. Return two variations, one structured by layer and one flat """
        gradients_by_layer, flat_gradients = tape.gradient(
            total_loss, (trainables_by_layer, flat_trainables))
        grads_and_vars = zip(flat_gradients, flat_trainables)
        return gradients_by_layer, grads_and_vars

    def _compute_total_loss(self, predictions_batch, targets_batch, losses):
        """ Compute the combined loss of all output layers """
        total_loss = tf.constant(0.0)
        individual_losses = {}

        for feature_name, loss_fn in losses.items():
            # TODO: weight the different losses (story 1542)

            individual_losses[feature_name] = loss_fn(
                tf.reshape(targets_batch[feature_name],
                           shape=predictions_batch[feature_name].shape),
                predictions_batch[feature_name]
            )
            total_loss += individual_losses[feature_name]

        return total_loss, individual_losses

    def _reset_tracked_values(self, initial_state=None):
        if initial_state is None:
            self._layer_outputs = {}
            self._layer_trainables = {}
            self._global_stats_tracker = GlobalStatsTracker()
            self._input_stats_tracker = SampleStatsTracker()
            self._prediction_stats_tracker = SampleStatsTracker()
            self._target_stats_tracker = SampleStatsTracker()
            self._gradient_stats_tracker = GradientStatsTracker()
        else:
            self._layer_outputs = initial_state['layer_outputs']
            self._layer_trainables = initial_state['layer_trainables']
            self._global_stats_tracker = initial_state['global_stats_tracker']
            self._input_stats_tracker = initial_state['input_stats_tracker']
            self._prediction_stats_tracker = initial_state['prediction_stats_tracker']
            self._target_stats_tracker = initial_state['target_stats_tracker']
            self._gradient_stats_tracker = initial_state['gradient_stats_tracker']

        self._output_trackers = {}
        for layer_spec in self._graph_spec.target_layers:
            if initial_state is None:
                self._output_trackers[layer_spec.id_] = self._get_output_stats_tracker(layer_spec.datatype, layer_spec.feature_name)
            else:
                self._output_trackers[layer_spec.id_] = initial_state['output_trackers'][layer_spec.id_]

    def _get_output_stats_tracker(self, datatype, feature_name):
        if datatype == 'numerical':
            return NumericalOutputStatsTracker()
        elif datatype == 'categorical':
            return CategoricalOutputStatsTracker()
        elif datatype == 'binary':
            return CategoricalOutputStatsTracker()
        elif datatype == 'image':
            return ImageOutputStatsTracker()
        elif datatype == 'mask':
            return MaskOutputStatsTracker()

    def _update_tracked_values(
            self, trainables_by_layer, gradients_by_layer, final_and_intermediate_outputs_by_layer,
            inputs_batch, predictions_batch, targets_batch,
            total_loss, individual_losses, is_training, steps_completed
    ):
        """ Take a snapshot of the current tensors (e.g., layer weights) """

        self._layer_outputs = {}
        for layer_id in final_and_intermediate_outputs_by_layer.keys():
            self._layer_outputs[layer_id] = {
                name: tensor.numpy()
                for name, tensor in final_and_intermediate_outputs_by_layer[layer_id].items()
            }

        self._layer_trainables = {}
        for layer_id in trainables_by_layer.keys():
            self._layer_trainables[layer_id] = {
                name: tensor.numpy()
                for name, tensor in trainables_by_layer[layer_id].items()
            }

        self._global_stats_tracker.update(
            loss=total_loss,
            epochs_completed=self._num_epochs_completed,
            steps_completed=steps_completed,
            is_training=is_training
        )

        id_to_feature = {
            layer_spec.id_: layer_spec.feature_name
            for layer_spec in self._graph_spec.io_layers
        }

        self._input_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=inputs_batch)
        self._prediction_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=predictions_batch)
        self._target_stats_tracker.update(id_to_feature=id_to_feature, sample_batch=targets_batch)
        self._gradient_stats_tracker.update(gradients_by_layer=gradients_by_layer)

        for layer_spec in self._graph_spec.target_layers:
            tracker = self._output_trackers[layer_spec.id_]
            postprocessing = self._data_loader.get_postprocessing_pipeline(
                layer_spec.feature_name)

            tracker.update(
                inputs_batch=inputs_batch,
                predictions_batch=predictions_batch[layer_spec.feature_name],
                targets_batch=targets_batch[layer_spec.feature_name],
                epochs_completed=self._num_epochs_completed,
                loss=individual_losses[layer_spec.feature_name],
                postprocessing=postprocessing,
                steps_completed=steps_completed,
                is_training=is_training
            )

    def _collect_trainables_by_layer(self, model):
        """ Collect the trainable tensors from the model and structure them by layer """
        trainables_by_layer = {}
        for layer_id, layer in model.layers_by_id.items():
            if isinstance(layer, PerceptiLabsVisualizer):
                weights, bias = layer.visualized_trainables

                trainables = {}
                if isinstance(weights, tf.Variable):
                    trainables['weights'] = weights
                elif isinstance(weights, list):
                    trainables['weights'] = weights[0]
                if isinstance(bias, tf.Variable):
                    trainables['bias'] = bias

                if trainables:
                    trainables_by_layer[layer_id] = trainables

            elif len(layer.trainable_variables) > 0:
                logger.warning(
                    "Layer {layer_id} has trainable variables but does not implement the PerceptiLabsVisualizer abstract class. Weights, biases and derived quantities such as gradients will not be visualized correctly.")

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

        if self._user_email:
            tracking.send_training_stopped(
                self._user_email,
                self._model_id,
                self._graph_spec,
                self._training_time,
                self.progress,
                self.get_output_stats_summaries()
            )

    def headless_on(self):
        # TODO: implement (story 1545)
        pass

    def headless_off(self):
        # TODO: implement (story 1545)
        pass

    def close(self):
        self.stop()

    def get_layer_output(self, layer_id, output_variable='output'):
        """ Gets the output batch of a layer

        Arguments:
            layer_id: the layer id
            output_variable: which variable to fetch from the output dict
        Returns:
            A numpy array (or None if the layer/variable doesnt exist)
        """
        try:
            output_batch = self._layer_outputs[layer_id][output_variable]
            return output_batch
        except KeyError as e:
            return None

    def get_layer_weights(self, layer_id):
        """ Get the weights associated with a layer """
        try:
            value = self._layer_trainables[layer_id]['weights']
            return value
        except KeyError as e:
            return None

    def get_layer_bias(self, layer_id):
        """ Get the bias associated with a layer """
        try:
            value = self._layer_trainables[layer_id]['bias']
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
            'target_stats': self.get_target_stats(),
            'output_stats': self.get_output_stats(),
            'global_stats': self.get_global_stats()
        }
        #dict_ = {}
        t1 = time.perf_counter()
        logger.debug(f"get_results finished. Duration: {t1 - t0}")
        return dict_

    def get_global_stats(self):
        """ Returns a stats object for the current global stats """
        return self._global_stats_tracker.save()

    def get_target_stats(self) -> SampleStats:
        """ Returns a stats object for the current target values """
        return self._target_stats_tracker.save()

    def export(self, export_directory, mode='Standard'):
        if self._exporter is None:
            logger.warning("Exporter not set, couldn't export!")
            return
        
        if mode == 'Checkpoint':
            self._exporter.export_checkpoint(
                os.path.join(export_directory, 'checkpoint.ckpt'))
        else:
            self._exporter.export(export_directory)

    def export_inference(self, path, mode):
        if self._exporter is not None:
            self._exporter.export(path, mode)
        else:
            logger.warning(
                "Exporter not set, couldn't export inference model!")

    def export_checkpoint(self, path):
        if self._exporter is not None:
            path = os.path.join(path, 'checkpoint.ckpt')
            self._exporter.export_checkpoint(path)
        else:
            logger.warning("Exporter not set, couldn't export checkpoint!")

    def get_output_stats(self) -> Dict:
        """ Returns a stats object representing the current state of the outputs """
        output_stats = {
            layer_id: tracker.save()
            for layer_id, tracker in self._output_trackers.items()
        }
        return output_stats

    def get_output_stats_summaries(self):
        """ Collect summary dicts from all output layers and add them to a list """
        all_output_stats = self.get_output_stats()

        all_summaries = []
        for output_stats in all_output_stats.values():
            summary = output_stats.get_summary()
            all_summaries.append(summary)

        return all_summaries

    def _resolve_optimizer(self, training_settings):
        optimizer = training_settings['Optimizer']
        learning_rate = training_settings['Learning_rate']
        momentum = training_settings['Momentum']
        beta_1 = training_settings['Beta1']
        beta_2 = training_settings['Beta2']
        centered = training_settings['Centered']

        if isinstance(learning_rate, str):
            learning_rate = float(learning_rate)
        if isinstance(momentum, str):
            momentum = float(momentum)
        if isinstance(beta_1, str):
            beta_1 = float(beta_1)
        if isinstance(beta_2, str):
            beta_2 = float(beta_2)

        if optimizer == 'SGD':
            return tf.keras.optimizers.SGD(learning_rate=learning_rate, momentum=momentum)
        elif optimizer == 'ADAM':
            return tf.keras.optimizers.Adam(learning_rate=learning_rate, beta_1=beta_1, beta_2=beta_2)
        elif optimizer == 'Adagrad':
            return tf.keras.optimizers.Adagrad(learning_rate=learning_rate)
        elif optimizer == 'RMSprop':
            return tf.keras.optimizers.RMSprop(learning_rate=learning_rate, centered=centered)

    def _resolve_loss_function(self, training_settings):
        loss = training_settings['Loss']
        if loss == 'Quadratic':
            return tf.keras.losses.MeanSquaredError()
        elif loss == 'Cross-Entropy':
            return tf.keras.losses.CategoricalCrossentropy()
        elif loss == 'Dice':
            return dice


    def _setup_loss_functions(self, training_settings):
        """ Creates a dict of losses, one per output """
        loss_function = self._resolve_loss_function(training_settings)

        losses = {
            layer_spec.feature_name: loss_function
            for layer_spec in self._graph_spec.layers
            if layer_spec.is_target_layer
        }
        return losses

    def _get_training_set(self):
        """ Gets a training set matching the training settings """
        return self._get_dataset('training', shuffle=self._shuffle_training_set)        

    def _get_validation_set(self):
        """ Gets a validation set matching the training settings """
        return self._get_dataset('validation', shuffle=False)

    def _get_dataset(self, partition, shuffle):
        indexed_dataset = self._data_loader.get_dataset(
            partition=partition,
            shuffle=shuffle,
            drop_index=False  # Drop the index manually so we can inspect the rows used
        )

        if settings.TRAINING_DUMP_ROWS is not None:
            self._dump_dataset_rows(partition, indexed_dataset)

        dataset = self._data_loader \
                      .drop_dataset_index(indexed_dataset) \
                      .batch(self.batch_size)
        return dataset
        

    def _dump_dataset_rows(self, partition, indexed_dataset):
        indices = [row.numpy() for row, _, _, in indexed_dataset]

        df = self._data_loader.get_data_frame(partition='original')
        df = df.iloc[indices]

        path = f"data_epoch_{self._num_epochs_completed}_{partition}.csv"
        df.to_csv(path, index=True)
        logger.info(f"Saved data dump to {path}")
        
        
