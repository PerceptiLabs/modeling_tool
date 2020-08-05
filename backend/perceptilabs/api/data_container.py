import logging
import pandas as pd
import numpy as np
import psutil
from typing import List

from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.logconf import APPLICATION_LOGGER, DATA_LOGGER
from perceptilabs.utils import get_object_size

logger = logging.getLogger(APPLICATION_LOGGER)
data_logger = logging.getLogger(DATA_LOGGER)

class DataContainer:
    def __init__(self):
        '''Initializes data_container to store experiments. Datacontainer will also track
        internal memory usage along with a max threshold'''
        self.experiments = {}
        self.obj_ids = set()
        self.memory_usage = 0

        # Utilizing a max threshold of 25% of total memory for DataContainer
        self.MAX_THRESHOLD = (psutil.virtual_memory().total/1e6) * 0.25

    def get_experiment(self, experiment_name: str) -> dict:
        '''Gets the saved experiment based on name of experiment

        Args:
            experiment_name: name of experiment

        Returns:
            experiment: Dictionary of saved experiment
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment {0} does not exist".format(experiment_name))

        return self.experiments[experiment_name]

    def get_experiment_names(self) -> List[str]:
        '''Gets the name of all the experiments being saved

        Returns:
            names: a list of experiment names
        '''
        names = list(self.experiments.keys())

        return names

    def process_message(self, raw_message: dict):
        '''Processes incoming messages to be stored. Data will be stored
        into correct experiment_name, then by category.
        
        Args:
            raw_message: a dictionary containing message to be processe
        '''
        self._process_incoming_message(raw_message)

    def _process_incoming_message(self, raw_message: dict):
        '''Processes incoming message to be stored. Adds data into correct experiment and
        logs amount of memory used by data.

        Args:
            raw_message: a dictionary containing message to be processed
        '''
        message = deserialize(raw_message)

        if message:
            experiment_name = message['experiment_name']

            if experiment_name not in self.experiments:
                self.experiments[experiment_name] = {
                    'Experiment_name': experiment_name,
                    'Hyperparameters': {},
                    'Metrics': {}
                }

                self._track_memory(experiment_name)
                self._track_memory(self.experiments[experiment_name])

            if message['category'] == 'Metrics':
                name = message['name']
                metric = message['metric']
                step = message['step']

                if name not in self.experiments[experiment_name]['Metrics']:
                    self.experiments[experiment_name]['Metrics'][name] = pd.DataFrame(columns=(name, 'Step'))

                    self._track_memory(name)
                    self._track_memory(self.experiments[experiment_name]['Metrics'][name])

                if step is not None:
                    df = self.experiments[experiment_name]['Metrics'][name]

                    item = {name: [metric], 'Step': [step]}

                    df_item = pd.DataFrame(item)

                    self.experiments[experiment_name]['Metrics'][name] = pd.concat([df, df_item], ignore_index=True)
                    self._track_memory(item)
                    self._clean_mem([df, df_item])
                else:
                    df = self.experiments[experiment_name]['Metrics'][name]
                    step_list = set(df['Step'].tolist())

                    if step_list:
                        end = max(step_list) + 1
                    else:
                        end = 0

                    item = {name: [metric], 'Step': [end]}
                    df_item = pd.DataFrame(item)

                    self.experiments[experiment_name]['Metrics'][name] = pd.concat([df, df_item], ignore_index=True)
                    self._track_memory(item)
                    self._clean_mem([df, df_item, step_list])
            elif message['category'] == 'Hyperparameters':
                hyper_params = message['hyper_params']

                for hyper_param, value in hyper_params.items():
                    self.experiments[experiment_name]['Hyperparameters'][hyper_param] = value
                
                self._track_memory(hyper_params)
            
            self._check_memory()

    def get_hyperparameter_names(self, experiment_name: str) -> List[str]:
        '''Gets hyperparameters names returned as list

        Args:
            experiment_name: name of experiment to grab hyperparameters

        Returns:
            hyperparameters_names: list of all hyperparameter names logged in experiment
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        hyperparameters_names = list(self.experiments[experiment_name]['Hyperparameters'].keys())

        return hyperparameters_names

    def get_hyperparameter(self, experiment_name: str, hyper_param: str) -> any:
        '''Gets hyperparameters from given experiment name

        Args:
            experiment_name: name of the experiment to get hyperparameters from
            hyper_param: name of hyperparameter to search for

        Returns:
            hyper_param_val: hyperparameter value to be returned
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        if hyper_param not in self.experiments[experiment_name]['Hyperparameters']:
            raise ValueError("Hyperparameter: {0} does not exist in Experiment: {1}".format(hyper_param, experiment_name))

        hyper_param_val = self.experiments[experiment_name]['Hyperparameters'][hyper_param]

        return hyper_param_val

    def get_hyperparameters(self, experiment_name: str) -> dict:
        '''Gets all hyperparameters in the given experiment
        
        Args:
            experiment_name: name of the given experiment
        
        Returns:
            hyper_params: dictionary of all hyperparameters in the given experiment
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        hyper_params = self.experiments[experiment_name]['Hyperparameters']

        return hyper_params


    def get_metric_names(self, experiment_name: str) -> List[str]:
        '''Gets all metric names in the given experiment
        
        Args:
            experiment_name: name of the experiment to get data from
        
        Returns:
            metric_names: name of all the metrics in the given experiment
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        metric_names = list(self.experiments[experiment_name]['Metrics'].keys())

        return metric_names

    def get_metric(self, experiment_name: str, metric_name: str, start: int = 0, end: int = None) -> List[np.ndarray]:
        '''Gets metric from given experiment name and grabs data based on step range. If end
        is none, then mark end as end of list.

        Args:
            experiment_name: name of the experiment to get data from
            metric_name: name of the metric
            start: starting step
            end: ending step

        Returns:
            metrics: list of metrics (np.ndarray) sorted by step range (inclusive)
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        if metric_name not in self.experiments[experiment_name]['Metrics']:
            metrics = [np.nan]

            return metrics

        df = self.experiments[experiment_name]['Metrics'][metric_name]

        metrics = self._check_missing_vals(df, metric_name)
        self.experiments[experiment_name]['Metrics'][metric_name] = metrics

        if not end:
            end = max(set(metrics['Step'].tolist()))

        if end < 0:
            metrics = metrics.sort_values(['Step'], ascending=[True])[metric_name][end:].to_numpy()

            if len(metrics) < abs(end):
                full_metrics = np.empty(abs(end))
                full_metrics.fill(np.nan)

                full_metrics[:len(metrics)] = metrics
                metrics = full_metrics

                self._clean_mem([full_metrics])
        else:
            metrics = metrics.loc[metrics['Step'].between(start, end, inclusive=True)]
            metrics = metrics.sort_values(['Step'], ascending=[True])[metric_name].to_numpy()

            if len(metrics) < (end - start + 1):
                full_metrics = np.empty((end - start + 1))
                full_metrics.fill(np.nan)

                full_metrics[:len(metrics)] = metrics
                metrics = full_metrics

                self._clean_mem([full_metrics])

        return metrics

    def _clean_mem(self, del_list: list):
        '''Deletes and cleans up memory space

        Args:
            del_list: list of objects to be deleted
        '''
        del del_list

    def _check_missing_vals(self, df: pd.DataFrame, metric_name: str) -> pd.DataFrame:
        ''' Check for the missing values in the dataframe. If there are missing values,
        create NaN for missing values in dataframe.

        Args:
            df: dataframe to fill in missing values
            metric_name: name of metric column

        Returns:
            df: dataframe that contains all missing values
        '''
        current_vals = set(df['Step'].tolist())
        max_val = max(current_vals)
        full_vals = set([i for i in range(max_val + 1)])

        missing_vals = list(full_vals.difference(current_vals))

        if missing_vals:
            vals_into_df = [[np.nan, missing_val] for missing_val in missing_vals]

            df_vals = pd.DataFrame(vals_into_df, columns=[metric_name, 'Step'])
            df = pd.concat([df, df_vals], ignore_index=True)

            self._clean_mem([df_vals])

        return df
    
    def _track_memory(self, data_obj: any):
        '''Gets the current memory usage of data object and adds it to running total'''
        self.memory_usage += get_object_size(data_obj, self.obj_ids)
    
    def _check_memory(self):
        '''Checks the current memory usage of DataContainer. Log correct levels (info, warning) depending
        on how much memory is currently used.

        WARNING will display once memory crosses max threshold
        INFO will display once memory crosses 75% of max threshold
        '''
        memory_data = psutil.virtual_memory()
        phys_total = memory_data.total
        phys_available = memory_data.available

        if self.memory_usage/1e6 >= self.MAX_THRESHOLD:
            data_logger.warning(
                "dc_memory_used",
                phys_total=phys_total,
                phys_available=phys_available,
                dc_memory_usage=self.memory_usage,
                dc_total_memory=self.MAX_THRESHOLD
            )

        elif self.memory_usage/1e6 >= self.MAX_THRESHOLD * 0.75:
            data_logger.info(
                "dc_memory_used",
                phys_total=phys_total,
                phys_available=phys_available,
                dc_memory_usage=self.memory_usage,
                dc_total_memory=self.MAX_THRESHOLD
            )
    
    def _delete_experiment(self, experiment_name: str):
        '''Removes experiment from datacontainer and cleans up memory usage
        
        Args:
            experiment_name: name of experiment to delete
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))
        
        _ids = set()
        memory_used = get_object_size(self.experiments[experiment_name], _ids)

        self.obj_ids = self.obj_ids.difference(_ids)
        self.memory_usage -= memory_used

        del self.experiments[experiment_name]

    def _delete_all_experiments(self):
        '''Removes all experiment from datacontainer and resets memory usage'''
        del self.experiments, self.obj_ids, self.memory_usage

        self.experiments = {}
        self.obj_ids = set()
        self.memory_usage = get_object_size(self.experiments, self.obj_ids)
