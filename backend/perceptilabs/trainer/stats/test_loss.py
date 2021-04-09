import pytest
import numpy as np
from unittest.mock import MagicMock

from perceptilabs.trainer.stats.loss import LossStats
    
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

        
