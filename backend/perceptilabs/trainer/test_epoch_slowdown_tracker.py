import numpy as np
from perceptilabs.trainer.utils import EpochSlowdownTracker


def test_sudden_slowdown():
    est = EpochSlowdownTracker()

    for t in [1.0, 1.1, 1.0, 1.2, 1.3, 1.0, 7.0]:
        est.add_time(t)

    assert est.has_slowdown()


def test_gradual_slowdown():
    est = EpochSlowdownTracker()

    for x in range(100):
        y = 1.1*x
        est.add_time(y)

    assert est.has_slowdown()


def test_noisy_constant():
    np.random.seed(0)
    est = EpochSlowdownTracker()

    def maybe_add_shot_noise(probability):
        if np.random.random() < probability:
            return 1.0
        else:
            return 0.0
        
    for _ in range(400):
        y = 1.0 + maybe_add_shot_noise(probability=0.1)
        est.add_time(y)

    assert not est.has_slowdown()



    
