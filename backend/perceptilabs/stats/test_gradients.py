import pytest
import tensorflow as tf

from perceptilabs.stats.gradients import GradientStats, GradientStatsTracker


def test_stats_objects_are_equal_when_args_are_equal():
    min1 = [0.1, 0.2, 0.3]
    avg1 = [0.4, 0.5, 0.6]
    max1 = [0.5, 0.7, 0.8]    
    obj1 = GradientStats(minimum_series=min1, average_series=avg1, maximum_series=max1)

    min2 = [0.1, 0.2, 0.3]
    avg2 = [0.4, 0.5, 0.6]
    max2 = [0.5, 0.7, 0.8]    
    obj2 = GradientStats(minimum_series=min2, average_series=avg2, maximum_series=max2)

    min3 = [0.2, 0.2, 0.3]
    avg3 = [0.4, 0.5, 0.6]
    max3 = [0.5, 0.7, 0.8]    
    obj3 = GradientStats(minimum_series=min3, average_series=avg3, maximum_series=max3)
    assert obj1 == obj2 != obj3

    
def test_trackers_are_equal_when_both_are_updated():
    gradients = {
        'layer1': {'weights': tf.constant([[3.0, 4.0], [7.0, 8.0]]), 'bias': tf.constant(12.0)},
        'layer2': {'weights': tf.constant([[2.0, 3.0], [4.0, 6.0]]), 'bias': tf.constant(13.0)}
    }
    
    tracker1 = GradientStatsTracker()
    tracker2 = GradientStatsTracker()    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()    

    tracker1.update(gradients_by_layer=gradients)
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()    

    tracker2.update(gradients_by_layer=gradients)    
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()   

    
def test_serialized_trackers_are_equal():
    gradients = {
        'layer1': {'weights': tf.constant([[3.0, 4.0], [7.0, 8.0]]), 'bias': tf.constant(12.0)},
        'layer2': {'weights': tf.constant([[2.0, 3.0], [4.0, 6.0]]), 'bias': tf.constant(13.0)}
    }
    
    tracker1 = GradientStatsTracker()
    tracker1.update(gradients_by_layer=gradients)    
    data = tracker1.serialize()
    tracker2 = GradientStatsTracker.deserialize(data)
    assert tracker1 == tracker2
    
