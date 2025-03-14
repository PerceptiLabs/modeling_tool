import pytest
import tensorflow as tf


from perceptilabs.stats.accuracy import (
    AccuracyStats,
    PredictionMatrix,
    AccuracyStatsTracker,
)


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


def flatten_matrices(prediction_matrices, phase="both"):
    flattened = []
    for epoch_matrices in prediction_matrices:
        for matrix, is_training in epoch_matrices:
            if (is_training and phase in ["both", "training"]) or (
                not is_training and phase in ["both", "validation"]
            ):
                flattened.append(matrix)
    return flattened


def compute_accuracy(steps, phase="both"):
    correct, total = 0, 0
    for matrix, is_training in steps:
        if (is_training and phase in ["both", "training"]) or (
            not is_training and phase in ["both", "validation"]
        ):
            correct += matrix.correct
            total += matrix.total

    return correct / total


def test_epoch_accuracy_correct(prediction_matrices):
    stats = AccuracyStats(prediction_matrices)

    # Training
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase="training")
        actual = stats.get_average_accuracy_for_epoch(epoch, phase="training")
        assert actual == expected

    # Validation
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase="validation")
        actual = stats.get_average_accuracy_for_epoch(epoch, phase="validation")

    # Both
    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = compute_accuracy(epoch_matrices, phase="both")
        actual = stats.get_average_accuracy_for_epoch(epoch, phase="both")


def test_average_accuracy_over_epochs_training(prediction_matrices):
    expected = []
    for epoch_matrices in prediction_matrices:
        acc = compute_accuracy(epoch_matrices, phase="training")
        expected.append(acc)

    stats = AccuracyStats(prediction_matrices)
    actual = stats.get_accuracy_over_epochs(phase="training")


def test_average_accuracy_over_epochs_validation(prediction_matrices):
    expected = []
    for epoch_matrices in prediction_matrices:
        acc = compute_accuracy(epoch_matrices, phase="validation")
        expected.append(acc)

    stats = AccuracyStats(prediction_matrices)
    actual = stats.get_accuracy_over_epochs(phase="validation")


def test_accuracy_for_step(prediction_matrices):
    stats = AccuracyStats(prediction_matrices)

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        for step, (matrix, is_training) in enumerate(epoch_matrices):
            expected = matrix.correct / matrix.total

            actual = stats.get_accuracy_for_step(epoch, step)

            assert actual == expected


def test_accuracy_over_steps_training(prediction_matrices):
    stats = AccuracyStats(prediction_matrices)

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = []
        for step, (_, is_training) in enumerate(epoch_matrices):
            if is_training:
                acc = stats.get_accuracy_for_step(epoch, step)
                expected.append(acc)

        actual = stats.get_accuracy_over_steps(epoch, phase="training")
        assert actual == expected


def test_accuracy_over_steps_validation(prediction_matrices):
    stats = AccuracyStats(prediction_matrices)

    for epoch, epoch_matrices in enumerate(prediction_matrices):
        expected = []
        for step, (_, is_training) in enumerate(epoch_matrices):
            if not is_training:
                acc = stats.get_accuracy_for_step(epoch, step)
                expected.append(acc)

        actual = stats.get_accuracy_over_steps(epoch, phase="validation")
        assert actual == expected


def test_accuracy_for_latest_step_both(prediction_matrices):
    matrix = flatten_matrices(prediction_matrices)[-1]
    expected = matrix.correct / matrix.total

    stats = AccuracyStats(prediction_matrices)
    actual = stats.get_accuracy_for_latest_step()
    assert actual == expected


def test_accuracy_for_latest_step_training(prediction_matrices):
    matrix = flatten_matrices(prediction_matrices, phase="training")[-1]
    expected = matrix.correct / matrix.total

    stats = AccuracyStats(prediction_matrices)
    actual = stats.get_accuracy_for_latest_step(phase="training")
    assert actual == expected


def test_accuracy_for_latest_step_validation(prediction_matrices):
    matrix = flatten_matrices(prediction_matrices, phase="validation")[-1]
    expected = matrix.correct / matrix.total

    stats = AccuracyStats(prediction_matrices)
    actual = stats.get_accuracy_for_latest_step(phase="validation")
    assert actual == expected


def test_stats_objects_are_equal_when_args_are_equal():
    pm1 = [
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
        ]
    ]
    pm2 = [
        [
            (PredictionMatrix(correct=10, incorrect=12), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
        ]
    ]
    pm3 = [
        [
            (PredictionMatrix(correct=10, incorrect=11), True),
            (PredictionMatrix(correct=12, incorrect=9), True),
        ]
    ]

    obj1 = AccuracyStats(prediction_matrices=pm1)
    obj2 = AccuracyStats(prediction_matrices=pm2)
    obj3 = AccuracyStats(prediction_matrices=pm3)
    assert obj1 == obj2 != obj3


def test_trackers_are_equal_when_both_are_updated():
    tracker1 = AccuracyStatsTracker()
    tracker2 = AccuracyStatsTracker()
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()

    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        epochs_completed=0,
        steps_completed=0,
        is_training=True,
    )
    assert tracker1 != tracker2
    assert tracker1.save() != tracker2.save()

    tracker2.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        epochs_completed=0,
        steps_completed=0,
        is_training=True,
    )
    assert tracker1 == tracker2
    assert tracker1.save() == tracker2.save()


def test_serialized_trackers_are_equal():
    tracker1 = AccuracyStatsTracker()
    tracker1.update(
        predictions_batch=tf.constant([[0, 0.1, 0.9], [1, 0, 0]]),
        targets_batch=tf.constant([[0, 1, 0], [1, 0, 0]]),
        epochs_completed=0,
        steps_completed=0,
        is_training=True,
    )
    data = tracker1.serialize()
    tracker2 = AccuracyStatsTracker.deserialize(data)
    assert tracker1 == tracker2
