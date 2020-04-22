import pytest
import numpy as np


from perceptilabs.core_new.cache2 import LightweightCache


@pytest.fixture(scope='function')
def cache():
    yield LightweightCache()


def test_put_get_returns_value(cache):
    value = np.array(123)
    cache.put('123', value, {'123': '<code123>'}, [])
    assert cache.get('123', {'123': '<code123>'}, []) == value

    
def test_put_get_returns_none_when_code_changed(cache):
    value = np.array(123)    
    id_to_code_1 = {'123': '<code123_1>'}
    id_to_code_2 = {'123': '<code123_2>'}    
    
    cache.put('123', value, id_to_code_1, [])
    assert cache.get('123', id_to_code_1, []) == value    
    assert cache.get('123', id_to_code_2, []) is None

    
def test_put_get_returns_none_when_ancestor_changed(cache):
    value = np.array(123)        
    id_to_code_1 = {'123': '<code123_1>', '456': '<code456_1>'}
    id_to_code_2 = {'123': '<code123_1>', '456': '<code456_2>'}    
    edges_by_id = [('456', '123')]
    
    cache.put('123', value, id_to_code_1, edges_by_id)
    assert cache.get('123', id_to_code_1, edges_by_id) == value    
    assert cache.get('123', id_to_code_2, edges_by_id) is None

    
def test_put_get_returns_value_when_unrelated_changed(cache):
    value = np.array(123)            
    id_to_code_1 = {'123': '<code123_1>', '456': '<code456_1>'}
    id_to_code_2 = {'123': '<code123_1>', '456': '<code456_2>'}    
    edges_by_id = []
    
    cache.put('123', value, id_to_code_1, edges_by_id)
    assert cache.get('123', id_to_code_2, edges_by_id) == value

    
def test_repeated_put_has_no_effect_on_size(cache):
    value = np.array(123)                
    cache.put('123', value, {'123': '<code123>'}, [])
    cache.put('123', value, {'123': '<code123>'}, [])    
    assert cache.size == 1


def test_evicts_last_gotten_when_size_exceeded():
    cache = LightweightCache(max_size=2)    
    value1 = np.array(123)
    value2 = np.array(456)
    value3 = np.array(789)                            
    
    cache.put('value1', value1, {'value1': '<code123>'}, [])
    cache.put('value2', value2, {'value2': '<code456>'}, [])    

    assert cache.size == 2
    assert cache.get('value2', {'value2': '<code456>'}, []) == value2
    assert cache.get('value1', {'value1': '<code123>'}, []) == value1

    cache.put('value3', value3, {'value3': '<code789>'}, [])
    assert cache.size == 2    
    assert cache.get('value2', {'value2': '<code456>'}, []) is None
    

    
    

    

    
