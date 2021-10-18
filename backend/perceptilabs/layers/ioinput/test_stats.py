import pickle
import numpy as np
import tensorflow as tf

from perceptilabs.layers.ioinput.stats import InputStats, InputStatsTracker


def test_stats_objects_are_equal_when_args_are_equal():
    batch1 = tf.constant([[10, 20], [20, 30], [30, 30.0]])
    obj1 = InputStats(inputs=batch1)

    batch2 = tf.constant([[10, 20], [20, 30], [30, 30.0]])
    obj2 = InputStats(inputs=batch2)

    batch3 = tf.constant([[10, 20], [20, 30], [30, 30.1]])
    obj3 = InputStats(inputs=batch3)
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
    batch = tf.constant([[10, 20], [20, 30], [30, 30.0]])
    
    tracker1 = InputStatsTracker()
    tracker2 = InputStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(inputs_batch=batch)
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(inputs_batch=batch)    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    batch = tf.constant([[10, 20], [20, 30], [30, 30.0]])
    
    tracker1 = InputStatsTracker()
    tracker1.update(inputs_batch=batch)
    
    data = tracker1.serialize()
    tracker2 = InputStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
    
                        

                                                                     
                                                             
