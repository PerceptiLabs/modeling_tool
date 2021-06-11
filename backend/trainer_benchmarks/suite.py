import time
import tensorflow as tf
from abc import ABC, abstractmethod


from perceptilabs.data.base import DataLoader
from perceptilabs.trainer.base import Trainer, TrainingModel
from perceptilabs.script import ScriptFactory
import perceptilabs.automation.utils as automation_utils


COLOR_WARNING = '\033[93m'
COLOR_DEFAULT = '\033[0m'


class BenchmarkSuite(ABC):
    def __init__(self):
        self.data_loader = None

    def _run_recommended_model(self):
        """ Trains the recommended model and collects the results """
        script_factory = ScriptFactory()

        if self.data_loader is None:
            raise ValueError("Data loader must be instantiated")

        graph_spec, training_settings = automation_utils.get_model_recommendation(self.data_loader)
        training_model = TrainingModel(script_factory, graph_spec)
        trainer = Trainer(self.data_loader, training_model, training_settings)

        t0 = time.perf_counter()        
        trainer.run()
        dt = time.perf_counter() - t0

        results = self._get_recommended_results(trainer, training_settings, dt)
        return results

    def get_results(self, which='both'):
        """ Pairs results from recommended model and keras baseline 
        
        Arguments:
            which: can be 'both', 'recommended' or 'baseline'.

        Returns:
            a dictionary of metrics and their values
        """
        recommended_results = self._run_recommended_model() if which in ['both', 'recommended'] else {}
        baseline_results = self._run_baseline_model() if which in ['both', 'baseline'] else {}

        metrices = set()
        metrices.update(recommended_results)
        metrices.update(baseline_results)        
        
        results = {}
        for metric in sorted(metrices):
            if which == 'both' and metric not in baseline_results:
                print(f"{COLOR_WARNING}Warning:{COLOR_DEFAULT} metric '{metric}' in recommended, but not in baseline results")
            if which == 'both' and metric not in recommended_results:
                print(f"{COLOR_WARNING}Warning:{COLOR_DEFAULT} metric '{metric}' in baseline, but not in recommended results")
            results[metric] = (baseline_results.get(metric), recommended_results.get(metric))
            
        return results

    @abstractmethod
    def _get_recommended_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model. The output dict should match the baseline 

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds
        
        Returns:
            a dictionary of metrics and their values
        """
        raise NotImplementedError

    @abstractmethod
    def _run_baseline_model(self, trainer, training_settings, training_duration):
        """ This trains a stand-alone baseline. E.g., an optimal Keras baseline. The output dict should match the recommended model

        Returns:
            a dictionary of metrics and their values
        """
        raise NotImplementedError
