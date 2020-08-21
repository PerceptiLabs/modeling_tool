import pytest
import numpy as np


from perceptilabs.core_new.cache2 import LightweightCache


@pytest.fixture(scope='function')
def cache():
    yield LightweightCache()


def test_put_get_returns_value(cache):
    expected = np.array(123)    
    
    cache.put('123', expected)
    actual = cache.get('123')
    assert actual == expected
    
    
def test_repeated_put_has_no_effect_on_size(cache):
    value = np.array(123)
    cache.put('123', value)
    cache.put('123', value)
    assert cache.size == 1


def test_evicts_last_gotten_when_size_exceeded():
    cache = LightweightCache(max_size=2)    
    value1 = np.array(123)
    value2 = np.array(456)
    value3 = np.array(789)                            
    
    cache.put('value1', value1)
    cache.put('value2', value2)    

    assert cache.size == 2
    assert cache.get('value2') == value2
    assert cache.get('value1') == value1

    cache.put('value3', value3)
    assert cache.size == 2    
    assert cache.get('value2') is None
    

    
    

    

    
