import numpy as np
import pytest
import os
from unittest.mock import MagicMock
from queue import Queue

import tensorflow as tf

from perceptilabs.call_context import CallContext
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.data.utils.builder import DatasetBuilder
from perceptilabs.data.settings import Partitions
from perceptilabs.testing_interface import TestingSessionInterface
from perceptilabs.script.base import ScriptFactory
from perceptilabs.rygg import RyggWrapper
from perceptilabs.resources.tf_support_access import TensorflowSupportAccess


def make_session_id(string):
    import base64

    return base64.urlsafe_b64encode(string.encode()).decode()


@pytest.fixture
def data_loader():
    builder = DatasetBuilder.from_features(
        {
            "x": {"datatype": "numerical", "iotype": "input"},
            "y": {"datatype": "categorical", "iotype": "target"},
        }
    )
    num_samples = 4
    with builder:
        for _ in range(num_samples):
            builder.add_row({"x": 1.0, "y": "a"})

        yield builder.get_data_loader()


@pytest.fixture
def image_loader():
    builder = DatasetBuilder.from_features(
        {
            "x": {"datatype": "image", "iotype": "input"},
            "y": {"datatype": "categorical", "iotype": "target"},
        },
        partitions=Partitions(training_ratio=0.1, validation_ratio=0.1, test_ratio=0.8),
    )

    categories = ["cat", "dog"]

    n_samples = 150
    with builder:
        for i in range(n_samples):
            with builder.create_row() as row:
                image = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
                row.file_data["x"] = image
                row.file_type["x"] = ".png"
                row.literals["y"] = categories[i % 2]

        data_loader = builder.get_data_loader()
        yield data_loader


@pytest.fixture()
def training_model():
    import tensorflow as tf

    class TrainingModel(tf.keras.Model):
        def call(self, inputs, training=False):

            y = inputs["x"]
            outputs = {"y": y}
            outputs_by_layer = {"layer1": inputs["x"]}

            return (outputs, outputs_by_layer)

    return TrainingModel()


@pytest.fixture(scope="function")
def image_model():
    import tensorflow as tf

    class TrainingModel(tf.keras.Model):
        def call(self, inputs, training=False):
            res = self.flatten(inputs["x"])
            res = self.dense(res)
            outputs_by_layer = {"layer1": inputs["x"]}
            outputs = {"y": res}
            return (outputs, outputs_by_layer)

        def build(self, input_shapes):
            self.flatten = tf.keras.layers.Flatten()
            self.dense = tf.keras.layers.Dense(2, activation="softmax")

    return TrainingModel()


@pytest.fixture(scope="function")
def queue():
    return Queue()


@pytest.fixture(scope="function")
def message_broker(queue):
    broker = MagicMock()
    broker.subscription.return_value.__enter__.return_value = queue
    yield broker


@pytest.mark.parametrize("results_interval", [None, 0.0001])
def test_results_are_stored(
    message_broker,
    data_loader,
    training_model,
    results_interval,
    temp_path,
    tensorflow_support_access,
):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    results_access = MagicMock()
    event_tracker = MagicMock()

    dataset_access = MagicMock()
    dataset_access.get_data_loader.return_value = data_loader

    preprocessing_results_access = MagicMock()

    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        results_access,
        tensorflow_support_access,
        preprocessing_results_access,
    )

    tests = ["confusion_matrix"]

    interface.run(
        call_context=CallContext(
            {
                "project_id": 123,
                "user_token": "fake token from auth header",
                "user_id": "a12312",
            }
        ),
        testing_session_id="123",
        models={
            "111": {
                "graphSettings": MagicMock(),
                "datasetSettings": MagicMock(),
                "model_name": "model111",
                "training_session_id": "134",
            }
        },
        tests=tests,
        results_interval=results_interval,
    )

    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][1]["status"]["status"] == "Completed"
    for test in tests:
        assert results_access.store.call_args[0][1]["results"][test] != {}


def test_stopping_mid_training(
    monkeypatch,
    queue,
    message_broker,
    data_loader,
    training_model,
    temp_path,
    tensorflow_support_access,
):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    dataset_access = MagicMock()
    dataset_access.get_data_loader.return_value = data_loader

    results_access = MagicMock()
    event_tracker = MagicMock()

    preprocessing_results_access = MagicMock()

    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        results_access,
        tensorflow_support_access,
        preprocessing_results_access,
    )

    tests = ["confusion_matrix"]

    testing_session_id = ("123",)

    step = interface.run_stepwise(
        CallContext({"user_email": "a@b.test"}),
        testing_session_id=testing_session_id,
        models={
            "111": {
                "graphSettings": MagicMock(),
                "datasetSettings": MagicMock(),
                "model_name": "model111",
                "training_session_id": make_session_id(temp_path),
            }
        },
        tests=tests,
    )

    for counter, _ in enumerate(step):
        if counter == 0:  # Stop after 3 steps
            expected_results = results_access.store.call_args[0][1]["results"]
            queue.put(
                {
                    "event": "testing-stop",
                    "payload": {"testing_session_id": testing_session_id},
                }
            )

    actual_results = results_access.store.call_args[0][1]["results"]

    assert counter > 0  # Assert we actuall went further than just the first iteration
    assert (
        actual_results == expected_results
    )  # Assert results doesnt change after stopping
    assert results_access.store.call_args[0][1]["status"]["status"] == "Stopped"


def test_tf_memory_growth_enabled(message_broker, data_loader, training_model):
    model_access = MagicMock()
    model_access.get_training_model.return_value = training_model

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    results_access = MagicMock()
    event_tracker = MagicMock()

    tf_support_access = MagicMock()
    tf_support_access.enable_tf_gpu_memory_growth.return_value = True

    dataset_access = MagicMock()
    dataset_access.get_data_loader.return_value = data_loader

    preprocessing_results_access = MagicMock()

    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        results_access,
        tf_support_access,
        preprocessing_results_access,
    )

    tests = ["confusion_matrix"]

    interface.run(
        call_context=CallContext(
            {
                "project_id": 123,
                "user_token": "fake token from auth header",
                "user_email": "a@b.test",
            }
        ),
        testing_session_id="123",
        models={
            "111": {
                "graphSettings": MagicMock(),
                "datasetSettings": MagicMock(),
                "model_name": "model111",
                "training_session_id": "134",
            }
        },
        tests=tests,
        results_interval=None,
    )

    assert tf_support_access.set_tf_dependencies.call_count > 0


def test_shap_results_are_stored(
    message_broker, image_loader, image_model, tensorflow_support_access
):
    model_access = MagicMock()
    model_access.get_training_model.return_value = image_model

    epochs_access = MagicMock()
    epochs_access.get_checkpoint_path.return_value = None

    results_access = MagicMock()
    event_tracker = MagicMock()

    dataset_access = MagicMock()
    dataset_access.get_data_loader.return_value = image_loader

    preprocessing_results_access = MagicMock()

    class Explainer:
        def shap_values(self, samples):
            return samples

    explainer_factory = MagicMock()
    explainer_factory.make.return_value = Explainer()

    interface = TestingSessionInterface(
        message_broker,
        event_tracker,
        dataset_access,
        model_access,
        epochs_access,
        results_access,
        tensorflow_support_access,
        preprocessing_results_access,
        explainer_factory=explainer_factory,
    )

    tests = ["shap_values"]

    interface.run(
        call_context=CallContext(
            {
                "project_id": 123,
                "user_token": "fake token from auth header",
                "user_id": "a12312",
            }
        ),
        testing_session_id="123",
        models={
            "111": {
                "graphSettings": MagicMock(),
                "datasetSettings": MagicMock(),
                "model_name": "model111",
                "training_session_id": "134",
            }
        },
        tests=tests,
    )

    assert results_access.store.call_count > 0
    assert results_access.store.call_args[0][1]["status"]["status"] == "Completed"
    for test in tests:
        assert results_access.store.call_args[0][1]["results"][test] != {}
