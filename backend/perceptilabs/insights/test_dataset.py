import pytest
import numpy as np
from perceptilabs.insights.dataset import DatasetDistribution


@pytest.fixture
def dataset_random():
    mat = np.random.normal(100, 50, (100, 28, 28)).astype(np.longdouble)
    return mat


@pytest.fixture
def dataset_linear():
    mat = np.vstack(np.ones((1, 28, 28))*i for i in range(100)).astype(np.longdouble)
    return mat


def batch_gen(dataset):
    batch_size = 16
    for i in range(0, len(dataset), batch_size):
        yield dataset[i:i+batch_size]

        
def test_sample_max(dataset_linear):
    dd = DatasetDistribution()
    for batch in batch_gen(dataset_linear):
        batches = {'layer1': batch}
        dd.draw_sample(batches)
        
    assert np.all(dd.sample_max['layer1'] == dataset_linear[-1])


def test_sample_min(dataset_linear):
    dd = DatasetDistribution()
    for batch in batch_gen(dataset_linear):
        batches = {'layer1': batch}
        dd.draw_sample(batches)
        
    assert np.all(dd.sample_min['layer1'] == dataset_linear[0])

    
def test_shape_ok(dataset_random):
    dd = DatasetDistribution()
    for batch in batch_gen(dataset_random):
        batches = {'layer1': batch}
        dd.draw_sample(batches)

    true_shape = dataset_random[0].shape
    assert dd.shape['layer1'] == true_shape
    
    
def test_distribution_ok(dataset_random):
    dd = DatasetDistribution()
    for batch in batch_gen(dataset_random):
        batches = {'layer1': batch}
        dd.draw_sample(batches)

    means, stddevs = dd.sample_distribution
    assert np.all(np.isclose(means['layer1'], dataset_random.mean(axis=0)))
    assert np.all(np.isclose(stddevs['layer1'], dataset_random.std(axis=0)))

    
    
    
    
