import pickle
import numpy as np
import tensorflow as tf

from perceptilabs.stats import SampleStats, SampleStatsTracker


def test_get_sample_by_id():
    batch = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}
    stats = SampleStats(
        id_to_feature={'layer1': 'x1'},        
        sample_batch=batch
    )

    expected = batch['x1'][-1]
    actual = stats.get_sample_by_layer_id('layer1')

    assert np.all(actual == expected)


def test_get_average_ok():
    batch = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}
    stats = SampleStats(
        id_to_feature={'layer1': 'x1'},
        sample_batch=batch
    )

    expected = np.average(batch['x1'], axis=0)    
    actual = stats.get_batch_average('layer1')

    assert np.all(actual == expected)



def test_stats_objects_are_equal_when_args_are_equal():
    batch1 = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}
    obj1 = SampleStats(sample_batch=batch1, id_to_feature={'layer1': 'x1'})        

    batch2 = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}        
    obj2 = SampleStats(sample_batch=batch2, id_to_feature={'layer1': 'x1'})

    batch3 = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.1]])}
    obj3 = SampleStats(sample_batch=batch3, id_to_feature={'layer1': 'x1'})    
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
    batch = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}
    id_to_feature = {'layer1': 'x1'}
    
    tracker1 = SampleStatsTracker()
    tracker2 = SampleStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(sample_batch=batch, id_to_feature=id_to_feature)
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(sample_batch=batch, id_to_feature=id_to_feature)    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    batch = {'x1': tf.constant([[10, 20], [20, 30], [30, 30.0]])}
    id_to_feature = {'layer1': 'x1'}
    
    tracker1 = SampleStatsTracker()
    tracker1.update(sample_batch=batch, id_to_feature=id_to_feature)
    
    data = tracker1.serialize()
    tracker2 = SampleStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
                        

                                                                     
                                                             
