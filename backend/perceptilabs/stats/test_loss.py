import pytest
import numpy as np
from unittest.mock import MagicMock

from perceptilabs.stats.loss import LossStats
    
@pytest.fixture
def losses():
    losses = []

    for epoch in range(3):
        losses.append([])
        
        for batch in range(4):  # Training steps
            losses[epoch].append((np.random.random(), True))

        for batch in range(2):  # Validation steps
            losses[epoch].append((np.random.random(), False))

    return losses


def flatten_losses(losses_, phase='both'):
    flattened = []
    for epoch_losses in losses_:
        for value, is_training in epoch_losses:
            if (
                    (is_training and phase in ['both', 'training']) or
                    (not is_training and phase in ['both', 'validation'])
            ):
                flattened.append(value)
    return flattened

        
def test_get_loss_for_step(losses):
    stats = LossStats(losses=losses)    

    for i, epoch_losses in enumerate(losses):
        for j, batch_losses in enumerate(epoch_losses):
            expected, _ = losses[i][j]
            actual = stats.get_loss_for_step(epoch=i, step=j)
            assert actual == expected

            
def test_get_loss_over_steps_training(losses):
    stats = LossStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = [
            loss
            for loss, is_training in losses[epoch]
            if is_training
        ]
        actual = stats.get_loss_over_steps(epoch, phase='training')
        assert actual == expected


def test_get_loss_over_steps_validation(losses):
    stats = LossStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = [
            loss
            for loss, is_training in losses[epoch]
            if not is_training
        ]
        actual = stats.get_loss_over_steps(epoch, phase='validation')
        assert actual == expected


def test_get_average_loss_for_epoch_training(losses):
    stats = LossStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = np.average([
            loss
            for loss, is_training in losses[epoch]
            if is_training
        ])
        actual = stats.get_average_loss_for_epoch(epoch, phase='training')
        assert actual == expected

        
def test_get_average_loss_for_epoch_validation(losses):
    stats = LossStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = np.average([
            loss
            for loss, is_training in losses[epoch]
            if not is_training
        ])
        actual = stats.get_average_loss_for_epoch(epoch, phase='validation')
        assert actual == expected


def test_loss_for_latest_step_both(losses):
    expected = flatten_losses(losses)[-1]
    
    stats = LossStats(losses)
    actual = stats.get_loss_for_latest_step()
    assert actual == expected
        

def test_loss_for_latest_step_training(losses):
    expected = flatten_losses(losses, phase='training')[-1]
    
    stats = LossStats(losses)
    actual = stats.get_loss_for_latest_step(phase='training')
    assert actual == expected


def test_loss_for_latest_step_validation(losses):
    expected = flatten_losses(losses, phase='training')[-1]
    
    stats = LossStats(losses)
    actual = stats.get_loss_for_latest_step(phase='training')
    assert actual == expected
    
    
