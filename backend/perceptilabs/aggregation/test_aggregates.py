import pytest
from unittest.mock import MagicMock
import numpy as np

import perceptilabs.aggregation.aggregates as aggs
from perceptilabs.aggregation import AggregationEngine
from perceptilabs.utils import DummyExecutor


@pytest.fixture
def data_container():
    container = MagicMock()
    yield container

    
@pytest.fixture
def engine(data_container):
    aggregates = {
        'average': aggs.AverageAggregate,
        'subtract': aggs.SubtractAggregate,
        'epoch-final-value': aggs.EpochFinalValue,            
        #'process_weights': None
    }
    
    executor = DummyExecutor()
    engine = AggregationEngine(executor, data_container, aggregates=aggregates)
    yield engine


def test_average_basic(data_container, engine):
    data_container.get_metric.return_value = [x for x in range(100)]
    expected = np.average(data_container.get_metric(), axis=0)
    
    future = engine.request('average', 'exp123', ['metric1'], 0, 100)
    actual, _, _ = future.result()

    assert actual == expected


def test_subtract_basic(data_container, engine):
    N = 100
    
    def get_metric(experiment_name, metric_name, start, end):
        if metric_name == 'metric1':
            return [1 + x for x in range(N)]
        else:
            return [x for x in range(N)]

    
    data_container.get_metric.side_effect = get_metric
    expected = np.ones((N, ))
    
    future = engine.request('subtract', 'exp123', ['metric1', 'metric2'], 0, N)
    actual, _, _ = future.result()

    assert np.all(actual == expected)
    
    
def test_epoch_final_value(data_container, engine):
    
    def get_metric(experiment_name, metric_name, start, end):
        if metric_name == 'epoch':
            return [0, 0, 0, 1, 1, 1, 2, 2, 2]
        else:
            return [1, 1, 2, 3, 3, 4, 5, 6, 7]
    
    data_container.get_metric.side_effect = get_metric

    future = engine.request('epoch-final-value', 'exp123', ['accuracy', 'epoch'], 0, 9)
    actual, _, _ = future.result()
    expected = [2, 4, 7]

    assert np.all(actual == expected)
    
    

    
    
    
