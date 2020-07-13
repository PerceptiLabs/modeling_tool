import logging
import pandas as pd
import numpy as np
from typing import List

from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

class DataContainer:
    def __init__(self):
        '''Initializes data_container'''
        self.experiments = {}

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
        '''Gets all the name of the experiments being saved

        Returns:
            names: a list of experiment names
        '''
        names = self.experiments.keys()

        return names

    def process_message(self, raw_message: dict):
        ''''''
        self._process_incoming_message(raw_message)

    def _process_incoming_message(self, raw_message: dict):
        '''Processes incoming message to be stored. Data will be stored
        into correct experiment_name, then by category.

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

            if message['category'] == 'Metrics':
                name = message['name']
                metric = message['metric']
                step = message['step']

                if name not in self.experiments[experiment_name]['Metrics']:
                    self.experiments[experiment_name]['Metrics'][name] = pd.DataFrame(columns=(name, 'Step'))

                if step is not None:
                    df = self.experiments[experiment_name]['Metrics'][name]

                    item = {name: [metric], 'Step': [step]}

                    df_item = pd.DataFrame(item)

                    self.experiments[experiment_name]['Metrics'][name] = pd.concat([df, df_item], ignore_index=True)
                    self._clean_df_mem([df, df_item])
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
                    self._clean_df_mem([df, df_item])
            elif message['category'] == 'Hyperparameters':
                hyper_params = message['hyper_params']

                for hyper_param, value in hyper_params.items():
                    self.experiments[experiment_name]['Hyperparameters'][hyper_param] = value

    def get_hyperparameter_names(self, experiment_name: str) -> List[str]:
        '''Gets hyperparameters names returned as list

        Args:
            experiment_name: name of experiment to grab hyperparameters

        Returns:
            hyperparameters_names: list of all hyperparameter names logged in experiment
        '''
        if experiment_name not in self.experiments:
            raise ValueError("Experiment: {0} does not exist".format(experiment_name))

        hyperparameters_names = self.experiments[experiment_name]['Hyperparameters'].keys()

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

    def get_metric(self, experiment_name: str, metric_name: str, start: int = 0, end: int = None) -> list:
        '''Gets metric from given experiment name and grabs data based on step range. If end
        is none, then mark end as end of list.

        Args:
            experiment_name: name of the experiment to get data from
            metric_name: name of the metric
            start: starting step
            end: ending step

        Returns:
            metrics: list of metrics sorted by step range (inclusive)
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
            metrics = metrics.sort_values(['Step'], ascending=[True])[metric_name].tolist()[end:]
        else:
            metrics = metrics.loc[metrics['Step'].between(start, end, inclusive=True)]
            metrics = metrics.sort_values(['Step'], ascending=[True])[metric_name].tolist()

        return metrics

    def _clean_df_mem(self, del_list: list):
        '''Deletes and cleans up memory space

        Args:
            del_list: list of dataframes to be deleted
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

            self._clean_df_mem([df_vals])

        return df
