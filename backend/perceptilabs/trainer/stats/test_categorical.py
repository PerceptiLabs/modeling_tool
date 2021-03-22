import pytest
import numpy as np
from unittest.mock import MagicMock


from perceptilabs.trainer.stats.categorical import CategoricalOutputStats, PredictionMatrix


@pytest.fixture
def prediction_matrices():
    epochs = [
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
            (PredictionMatrix(correct=13, incorrect=1), True),
            (PredictionMatrix(correct=14, incorrect=1), False),
            (PredictionMatrix(correct=15, incorrect=5), False),
        ],
        [
            (PredictionMatrix(correct=5, incorrect=9), True),
            (PredictionMatrix(correct=6, incorrect=13), True),
            (PredictionMatrix(correct=1, incorrect=12), True),
            (PredictionMatrix(correct=3, incorrect=11), False),
        ],
    ]
    yield epochs

    
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
        

def compute_accuracy(steps, phase='both'):
    correct, total = 0, 0
    for matrix, is_training in steps:
        if (
                (is_training and phase in ['both', 'training']) or
                (not is_training and phase in ['both', 'validation'])
        ):
            correct += matrix.correct 
            total += matrix.total
                
    return correct/total


def test_epoch_accuracy_correct(prediction_matrices):
    stats = CategoricalOutputStats(prediction_matrices)

    # Training
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase='training')
        actual = stats.get_average_accuracy_for_epoch(epoch, phase='training')
        assert actual == expected

    # Validation
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase='validation')
        actual = stats.get_average_accuracy_for_epoch(epoch, phase='validation')

    # Both
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase='both')
        actual = stats.get_average_accuracy_for_epoch(epoch, phase='both')
        
    
def test_average_accuracy_over_epochs_training(prediction_matrices):
    expected = []
    for epoch_matrices in prediction_matrices:
        acc = compute_accuracy(epoch_matrices, phase='training')
        expected.append(acc)
    
    stats = CategoricalOutputStats(prediction_matrices)
    actual = stats.get_average_accuracy_over_epochs(phase='training')

    
def test_average_accuracy_over_epochs_validation(prediction_matrices):
    expected = []
    for epoch_matrices in prediction_matrices:
        acc = compute_accuracy(epoch_matrices, phase='validation')
        expected.append(acc)
    
    stats = CategoricalOutputStats(prediction_matrices)
    actual = stats.get_average_accuracy_over_epochs(phase='validation')


def test_accuracy_for_step(prediction_matrices):
    stats = CategoricalOutputStats(prediction_matrices)    

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        for step, (matrix, is_training) in enumerate(epoch_matrices):
            expected = matrix.correct/matrix.total

            actual = stats.get_accuracy_for_step(epoch, step)

            assert actual == expected

            
def test_accuracy_over_steps_training(prediction_matrices):
    stats = CategoricalOutputStats(prediction_matrices)    

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = []            
        for step, (_, is_training) in enumerate(epoch_matrices):
            if is_training:
                acc = stats.get_accuracy_for_step(epoch, step)
                expected.append(acc)

        actual = stats.get_accuracy_over_steps(epoch, phase='training')
        assert actual == expected

        
def test_accuracy_over_steps_validation(prediction_matrices):
    stats = CategoricalOutputStats(prediction_matrices)    

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = []            
        for step, (_, is_training) in enumerate(epoch_matrices):
            if not is_training:
                acc = stats.get_accuracy_for_step(epoch, step)
                expected.append(acc)

        actual = stats.get_accuracy_over_steps(epoch, phase='validation')
        assert actual == expected

        
def test_get_loss_for_step(losses):
    stats = CategoricalOutputStats(losses=losses)    

    for i, epoch_losses in enumerate(losses):
        for j, batch_losses in enumerate(epoch_losses):
            expected, _ = losses[i][j]
            actual = stats.get_loss_for_step(epoch=i, step=j)
            assert actual == expected

            
def test_get_loss_over_steps_training(losses):
    stats = CategoricalOutputStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = [
            loss
            for loss, is_training in losses[epoch]
            if is_training
        ]
        actual = stats.get_loss_over_steps(epoch, phase='training')
        assert actual == expected


def test_get_loss_over_steps_validation(losses):
    stats = CategoricalOutputStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = [
            loss
            for loss, is_training in losses[epoch]
            if not is_training
        ]
        actual = stats.get_loss_over_steps(epoch, phase='validation')
        assert actual == expected


def test_get_average_loss_for_epoch_training(losses):
    stats = CategoricalOutputStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = np.average([
            loss
            for loss, is_training in losses[epoch]
            if is_training
        ])
        actual = stats.get_average_loss_for_epoch(epoch, phase='training')
        assert actual == expected

        
def test_get_average_loss_for_epoch_validation(losses):
    stats = CategoricalOutputStats(losses=losses)    

    for epoch, epoch_losses in enumerate(losses):
        expected = np.average([
            loss
            for loss, is_training in losses[epoch]
            if not is_training
        ])
        actual = stats.get_average_loss_for_epoch(epoch, phase='validation')
        assert actual == expected

        
            
