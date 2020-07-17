import time
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List, Tuple, Dict, Any
from concurrent.futures import Future, Executor



class Aggregate(ABC):
    @abstractmethod
    def _run_internal(self):
        raise NotImplementedError

    def run(self):
        try:
            result = self._run_internal()
        except:
            return None
        else:
            return result

    
AggregationRequest = namedtuple('AggregationRequest', ['result_name', 'aggregate_name', 'experiment_name', 'metric_names', 'start', 'end', 'aggregate_kwargs'])


def run_timed(func, t_queued, *args, **kwargs):
    t_started = time.perf_counter()
    queued = t_started - t_queued    
    
    result = func(*args, **kwargs)
    
    elapsed = time.perf_counter() - t_started
    return result, queued, elapsed


class AggregationEngine:
    def __init__(self, executor: Executor, data_container: 'DataContainer', aggregates: Dict[str, Aggregate] = None): 
        self._executor = executor
        self._data_container = data_container
        self._aggregates = aggregates.copy() if aggregates is not None else DEFAULT_AGGREGATES

    @property
    def aggregates(self) -> List[str]:
        """ List of available aggregates """
        return list(self._aggregates.keys())
    
    def request(self, aggregate_name: str, experiment_name: str, metric_names: List[str], start: int, end: int, aggregate_kwargs: Dict[str, Any] = None) -> Future:
        """ Performs an aggregation on a set of metrices.         

        Args:
            aggregate_name: the name of the aggregation to perform
            experiment_name: the name of the experiment
            metric_names: the names of the metrices. Will be used as positional arguments to the aggregate 
            start: starting step
            end: ending step
            aggregate_kwargs: a dictionary of values that will be passed as keyword arguments to the aggregate 

        Returns:
            A future returning a tuple with (result, time_queued, time_elapsed)
        """
        t_queued = time.perf_counter()
        if not aggregate_name in self._aggregates:
            raise ValueError(f"Invalid aggregate '{aggregate_name}'")

        # TODO(anton.k):
        # if queue times are high, pre-loading data could be a memory-bottleneck. Moving the get_metric call into the aggregate would probably help
        # however, for batch jobs this could cause out of sync because the data container might change between execution of requests.
        
        aggregate_args = [
            self._data_container.get_metric(experiment_name, metric_name, start, end)
            for metric_name in metric_names            
        ]
        aggregate_kwargs = aggregate_kwargs or {}
        aggregate = self._aggregates[aggregate_name](*aggregate_args, **aggregate_kwargs)

        future = self._executor.submit(run_timed, aggregate.run, t_queued)
        # TODO(anton.k): add callback for logging aggregate running times
        return future
            
    def request_batch(self, requests: List[AggregationRequest]) -> Future:
        """ Performs a batch of aggregations on a set of metrices.         

        Note: no guarantees are made about the data being consistent between aggregations.

        Args:
            requests: a list of AggregationRequests

        Returns:
            A future returning a tuple with (result, time_queued, time_elapsed)
        """
        t_queued = time.perf_counter()
        
        def wait_for_batch(futures):
            result = {result_name: future.result() for result_name, future in futures.items()}
            return result

        futures = {}
        for r in requests:
            futures[r.result_name] = self.request(
                r.aggregate_name,
                r.experiment_name,
                r.metric_names,
                r.start,
                r.end,
                aggregate_kwargs=r.aggregate_kwargs
            )

        future = self._executor.submit(run_timed, wait_for_batch, t_queued, futures)
        # TODO(anton.k): add callback for logging batch running times        
        return future
        



        

        
    

    
