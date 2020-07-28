import pytest
from unittest.mock import MagicMock
import numpy as np

from perceptilabs.aggregation.aggregates import AverageAggregate, MaxAggregate, MinAggregate, SubtractAggregate, EpochFinalValue, Identity, Transpose
from perceptilabs.aggregation import AggregationEngine
from perceptilabs.utils import DummyExecutor


@pytest.fixture
def data_container():
    container = MagicMock()
    yield container

    
@pytest.fixture
def engine(data_container):
    aggregates = {
        'average': AverageAggregate,
        'max': MaxAggregate,
        'min': MinAggregate,
        'subtract': SubtractAggregate,
        'epoch-final-value': EpochFinalValue,
        'identity': Identity,
        'transpose': Transpose
        #'process_weights': None
    }
    
    executor = DummyExecutor()
    engine = AggregationEngine(executor, data_container, aggregates=aggregates)
    yield engine


def test_average_basic(data_container, engine):
    data_container.get_metric.return_value = np.array([x for x in range(100)])
    expected = np.nanmean([data_container.get_metric()], axis=1)

    future = engine.request('average', 'exp123', ['metric1'], 0, 100)
    actual, _, _ = future.result()

    assert actual == expected


def test_max_basic(data_container, engine):
    data_container.get_metric.return_value = np.array([x if x % 2 == 0 else np.nan for x in range(100)])
    expected = np.nanmax([data_container.get_metric()], axis=1)

    future = engine.request('max', 'exp123', ['metric1'], 0, 100)
    actual, _, _ = future.result()

    assert actual == expected


def test_min_basic(data_container, engine):
    data_container.get_metric.return_value = np.array([x if x % 2 == 0 else np.nan for x in range(100)])
    expected = np.nanmin([data_container.get_metric()], axis=1)

    future = engine.request('min', 'exp123', ['metric1'], 0, 100)
    actual, _, _ = future.result()

    assert actual == expected


def test_subtract_basic(data_container, engine):
    N = 100
    
    def get_metric(experiment_name, metric_name, start, end):
        if metric_name == 'metric1':
            return np.array([1 + x for x in range(N)])
        else:
            return np.array([x for x in range(N)])

    
    data_container.get_metric.side_effect = get_metric
    expected = np.ones((N, ))
    
    future = engine.request('subtract', 'exp123', ['metric1', 'metric2'], 0, N)
    actual, _, _ = future.result()

    assert np.all(actual == expected)
    
    
def test_epoch_final_value(data_container, engine):
    
    def get_metric(experiment_name, metric_name, start, end):
        if metric_name == 'epoch':
            return np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        else:
            return np.array([1, 1, 2, 3, 3, 4, 5, 6, 7])
    
    data_container.get_metric.side_effect = get_metric

    future = engine.request('epoch-final-value', 'exp123', ['accuracy', 'epoch'], 0, 9)
    actual, _, _ = future.result()
    expected = np.array([2, 4, 7])

    assert np.all(actual == expected)


def test_identity_basic(data_container, engine):
    data_container.get_metric.return_value = np.array([x if x % 2 == 0 else np.nan for x in range(100)])
    expected = data_container.get_metric()

    future = engine.request('identity', 'exp123', ['metric1'], 0, 99)
    actual, _, _ = future.result()

    assert np.isclose(actual, expected, equal_nan=True).all()

def test_transpose_basic(data_container, engine):
    data_container.get_metric.return_value = np.array([[1,2,3], [4,5,6]])
    matrix = np.array([data_container.get_metric()])
    expected = matrix.transpose(0, 2, 1) 

    future = engine.request('transpose', 'exp123', ['metric1'], 0, 100)
    actual, _, _ = future.result()

    assert np.isclose(actual, expected).all()
    assert expected.shape == actual.shape
    
    

    
    
    
