import time
import tensorflow as tf
import os
import pkg_resources

from perceptilabs.script import ScriptFactory
from trainer_benchmarks.suite import BenchmarkSuite
import perceptilabs.data.utils as data_utils
from perceptilabs.trainer.base import Trainer, TrainingModel
from perceptilabs.graph.builder import GraphSpecBuilder


class CovidXraySuite(BenchmarkSuite):
    def __init__(self):
        self.data_loader = data_utils.get_covid19_loader()

    def _get_trainer_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model. The output dict should match the baseline 

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds

        Returns:
            a dictionary of metrics and their values
        """
        stats = next(iter(trainer.get_output_stats().values())
                     )  # This dataset has a single output
        results = stats.get_summary()
        results['training_duration (s)'] = training_duration
        results['epoch_duration (ms)'] = training_duration / \
            int(training_settings['Epochs']) * 1000
        results['num_epochs'] = int(training_settings['Epochs'])
        return results

    def _run_custom_model(self):
        path = os.path.join(data_utils.get_tutorial_data_directory(),
                            'Covid-19', 'data.csv')
        builder = GraphSpecBuilder()

        c1 = builder.add_layer('IoInput',
                               settings={'datatype': 'image', 'feature_name': 'images', 'file_path': path})
        c2 = builder.add_layer('PreTrainedVGG16', settings = {})
        c3 = builder.add_layer('DeepLearningFC',
                               settings={'n_neurons': 128, 'activation': 'ReLU', 'batch_norm': True, 'dropout': True, 'keep_prob': 0.5})
        c4 = builder.add_layer('DeepLearningFC',
                               settings={'n_neurons': 3, 'activation': 'Softmax'})
        c5 = builder.add_layer('IoOutput',
                               settings={'datatype': 'categorical', 'feature_name': 'labels', 'file_path': path})
        builder.add_connection(
            source_id=c1, source_var='output', dest_id=c2, dest_var='input')
        builder.add_connection(c2, 'output', c3, 'input')
        builder.add_connection(c3, 'output', c4, 'input')
        builder.add_connection(c4, 'output', c5, 'input')
        graph_spec = builder.build()

        training_settings = {'Epochs': '5',
                             'Batch_size': '8',
                             'Shuffle': True,
                             'Loss': 'Quadratic',
                             'Learning_rate': 0.001,
                             'Optimizer': 'ADAM',
                             'Beta1': 0.9,
                             'Beta2': 0.999,
                             'Momentum': 0,
                             'Centered': False,
                             'AutoCheckpoint': False}
        script_factory = ScriptFactory()
        training_model = TrainingModel(script_factory, graph_spec)
        trainer = Trainer(self.data_loader, training_model, training_settings)
        t0 = time.perf_counter()
        trainer.run()
        dt = time.perf_counter() - t0

        results = self._get_trainer_results(trainer, training_settings, dt)
        return results

    def _get_trainer_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model or custom model. The output dict should match the baseline

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds

        Returns:
            a dictionary of metrics and their values
        """
        stats = next(iter(trainer.get_output_stats().values())
                     )  # This dataset has a single output
        results = stats.get_summary()
        results['training_duration (s)'] = training_duration
        results['epoch_duration (ms)'] = training_duration / \
            int(training_settings['Epochs']) * 1000
        results['num_epochs'] = int(training_settings['Epochs'])
        return results
