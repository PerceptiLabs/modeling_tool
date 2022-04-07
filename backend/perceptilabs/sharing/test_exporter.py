import os
import pytest
import tempfile
from unittest.mock import MagicMock

import tensorflow as tf
import numpy as np
from fastapi.testclient import TestClient

from perceptilabs.trainer.model import TrainingModel
from perceptilabs.script import ScriptFactory
from perceptilabs.graph.builder import GraphSpecBuilder
from perceptilabs.sharing.exporter import Exporter
import perceptilabs.sharing.fastapi_utils as fastapi_utils
import perceptilabs.data.utils as data_utils
from perceptilabs.test_utils import make_data_loader


def join_and_sanitize(*args):
    path = os.path.join(*args)
    path = path.replace("\\", "/")
    return path


data0 = {
    "x1": {
        "type": "numerical",
        "values": [
            123.0,
            24.0,
            13.0,
            45.0,
            20.0,
            200.0,
            421.0,
            300.0,
            254.0,
            217.0,
            363.0,
            500.0,
        ],
    },
    "y1": {
        "type": "numerical",
        "values": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
    },
}


data1 = {
    "x1": {"type": "categorical", "values": ["cat", "house", "horse", "dog"]},
    "y1": {
        "type": "categorical",
        "values": ["animal", "non-animal", "animal", "animal"],
    },
}

data2 = {
    "x1": {
        "type": "image",
        "values": ["1.jpg", "2.jpg", "3.jpg", "5.jpg"],
        "shape": (16, 16, 3),
    },
    "y1": {
        "type": "categorical",
        "values": ["animal", "non-animal", "animal", "animal"],
    },
}

data3 = {
    "x1": {"type": "categorical", "values": [0, 1, 2, 3]},
    "y1": {"type": "categorical", "values": [1, 2, 0, 1]},
}


@pytest.fixture(params=[data0, data1, data2])
def data_loader(request):
    with make_data_loader(request.param) as dl:
        yield dl


@pytest.fixture(params=[data0, data1])
def data_loader_except_image(request):
    with make_data_loader(request.param) as dl:
        yield dl


@pytest.fixture()
def data_loader_numerical():
    with make_data_loader(data0) as dl:
        yield dl


@pytest.fixture()
def data_loader_categorical():
    with make_data_loader(data1) as dl:
        yield dl


@pytest.fixture()
def data_loader_image():
    with make_data_loader(data2) as dl:
        yield dl


def make_graph_spec(data_loader):
    gsb = GraphSpecBuilder()
    # Create the layers
    id1 = gsb.add_layer(
        "IoInput",
        settings={
            "datatype": data_loader.settings["x1"].datatype,
            "feature_name": "x1",
        },
    )

    if data_loader.settings["y1"].datatype == "categorical":
        n_neurons = len(
            data_loader.get_preprocessing_pipeline("y1").metadata["mapping"]
        )
    else:
        n_neurons = 1

    id2 = gsb.add_layer("DeepLearningFC", settings={"n_neurons": n_neurons})
    id3 = gsb.add_layer(
        "IoOutput",
        settings={
            "datatype": data_loader.settings["y1"].datatype,
            "feature_name": "y1",
        },
    )

    # Connect the layers
    gsb.add_connection(
        source_id=id1, source_var="output", dest_id=id2, dest_var="input"
    )
    gsb.add_connection(
        source_id=id2, source_var="output", dest_id=id3, dest_var="input"
    )

    graph_spec = gsb.build()
    return graph_spec


def equal_layer_outputs(dict1, dict2):
    """Checks if two layers have equal output"""
    if dict1.keys() != dict2.keys():
        return False

    for var_name in dict1.keys():
        values1 = dict1[var_name].numpy()
        values2 = dict2[var_name].numpy()

        if not np.all(values1 == values2):
            return False

    return True


def equal_training_model_outputs(all1, all2):
    """Checks if two training models have equal output"""
    output1, hidden1 = all1
    output2, hidden2 = all2

    if not equal_layer_outputs(output1, output2):
        return False

    if hidden1.keys() != hidden2.keys():
        return False

    for layer_id in hidden1.keys():
        if not equal_layer_outputs(hidden1[layer_id], hidden2[layer_id]):
            return False

    return True


def module_from_path(module_path, module_name="my_module"):
    import sys
    import importlib

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_create_exporter_from_graph(script_factory, data_loader):
    # Use data loader to feed data through the model
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    assert exporter is not None


def test_export_inference_model(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    on_exported = MagicMock()

    exporter = Exporter(
        graph_spec, training_model, data_loader, on_model_exported=on_exported
    )

    target_dir = join_and_sanitize(temp_path, "inference_model")
    assert not os.path.isdir(target_dir)

    expected_files = {
        "saved_model.pb",
        "keras_metadata.pb",
        "assets",
        "variables",
        join_and_sanitize("variables", "variables.index"),
        join_and_sanitize("variables", "variables.data-00000-of-00001"),
    }

    actual_files = set(exporter.export(target_dir, mode="Standard"))

    assert actual_files == expected_files
    assert all(os.path.exists(join_and_sanitize(target_dir, p)) for p in expected_files)
    assert on_exported.call_count == 1


def test_export_compressed_model(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    on_exported = MagicMock()
    exporter = Exporter(
        graph_spec, training_model, data_loader, on_model_exported=on_exported
    )

    target_dir = join_and_sanitize(temp_path, "inference_model")
    assert not os.path.isdir(target_dir)

    expected_files = {"model.tflite"}
    actual_files = set(exporter.export(target_dir, mode="Compressed"))

    assert actual_files == expected_files
    assert all(os.path.exists(join_and_sanitize(target_dir, p)) for p in expected_files)
    assert on_exported.call_count == 1


def test_export_quantized_model(script_factory, data_loader_numerical, temp_path):
    graph_spec = make_graph_spec(data_loader_numerical)
    training_model = TrainingModel(script_factory, graph_spec)
    on_exported = MagicMock()
    exporter = Exporter(
        graph_spec, training_model, data_loader_numerical, on_model_exported=on_exported
    )

    target_dir = join_and_sanitize(temp_path, "inference_model")
    assert not os.path.isdir(target_dir)

    expected_files = {"quantized_model.tflite"}
    actual_files = set(exporter.export(target_dir, mode="Quantized"))

    assert actual_files == expected_files
    assert all(os.path.exists(join_and_sanitize(target_dir, p)) for p in expected_files)
    assert on_exported.call_count == 1


def test_export_checkpoint_creates_files(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)

    exporter = Exporter(graph_spec, training_model, data_loader)

    target_dir = join_and_sanitize(temp_path, "checkpoint_dir")
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    checkpoint_path = join_and_sanitize(target_dir, "checkpoint.ckpt")
    exporter.export_checkpoint(checkpoint_path)
    ckpt = tf.train.latest_checkpoint(target_dir)
    assert ckpt is not None
    training_model.load_weights(ckpt).assert_consumed()


def test_export_checkpoint_creates_multiple_files(
    script_factory, data_loader, temp_path
):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)

    target_dir = join_and_sanitize(temp_path, "checkpoint_dir")
    assert not os.path.isdir(target_dir)
    assert tf.train.latest_checkpoint(target_dir) is None

    exporter.export_checkpoint(join_and_sanitize(target_dir, "checkpoint-0000.ckpt"))
    first_ckpt = tf.train.latest_checkpoint(target_dir)
    assert first_ckpt is not None
    training_model.load_weights(first_ckpt).assert_consumed()

    exporter.export_checkpoint(join_and_sanitize(target_dir, "checkpoint-0001.ckpt"))
    second_ckpt = tf.train.latest_checkpoint(target_dir)
    assert second_ckpt is not None
    assert second_ckpt != first_ckpt

    training_model.load_weights(
        second_ckpt
    ).assert_consumed()  # Make sure weights can be loaded
    training_model.load_weights(
        first_ckpt
    ).assert_consumed()  # Make sure 1st ckpt is still valid


def test_loading_different_checkpoints_consistent_results(
    script_factory, data_loader, temp_path
):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)

    exporter = Exporter(graph_spec, training_model, data_loader)
    target_dir = join_and_sanitize(temp_path, "checkpoint_dir")

    inputs, targets = data_loader.get_example_batch(2)

    # Infer and export for epoch 0
    expected_output_epoch_0 = training_model(inputs)
    exporter.export_checkpoint(join_and_sanitize(target_dir, "checkpoint-0000.ckpt"))
    ckpt_epoch_0 = tf.train.latest_checkpoint(target_dir)

    # Update the weights with random values to simulate a new epoch
    epoch_0_weights = training_model.get_weights()
    epoch_1_weights = [np.random.random() * w for w in epoch_0_weights]
    training_model.set_weights(epoch_1_weights)

    # Infer and export for epoch 1
    expected_output_epoch_1 = training_model(inputs)
    exporter.export_checkpoint(join_and_sanitize(target_dir, "checkpoint-0001.ckpt"))
    ckpt_epoch_1 = tf.train.latest_checkpoint(target_dir)

    # Check that two different checkpoints exist
    assert ckpt_epoch_0 != ckpt_epoch_1

    # Load weights from epoch 0 and check consistent output
    training_model.load_weights(ckpt_epoch_0)
    actual_output_epoch_0 = training_model(inputs)
    assert equal_training_model_outputs(actual_output_epoch_0, expected_output_epoch_0)

    # Load weights from epoch 1 and check consistent output
    training_model.load_weights(ckpt_epoch_1)
    actual_output_epoch_1 = training_model(inputs)
    assert equal_training_model_outputs(actual_output_epoch_1, expected_output_epoch_1)

    # Check that the models produced different outputs for each epoch
    assert not equal_training_model_outputs(
        actual_output_epoch_0, actual_output_epoch_1
    )
    assert not equal_training_model_outputs(
        expected_output_epoch_0, expected_output_epoch_1
    )


def test_inference_outputs_numerical(script_factory, data_loader_numerical):
    graph_spec = make_graph_spec(data_loader_numerical)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_numerical)
    inference_model = exporter.get_inference_model()

    x = {"x1": np.array([1.0, 2.0, 3.0])}
    y = inference_model(x)

    assert y["y1"].dtype == tf.float32
    assert y["y1"].shape == (3, 1)


def test_inference_retains_batch_size(script_factory, data_loader_except_image):
    graph_spec = make_graph_spec(data_loader_except_image)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_except_image)
    inference_model = exporter.get_inference_model()

    for batch_size in range(1, 4):
        inputs_batch, targets_batch = data_loader_except_image.get_example_batch(
            batch_size, apply_pipelines=None
        )

        assert targets_batch["y1"].shape[0] == inputs_batch["x1"].shape[0]

        outputs_batch = inference_model(inputs_batch)
        assert outputs_batch["y1"].shape[0] == inputs_batch["x1"].shape[0]


def test_inference_outputs_categorical(script_factory, data_loader_categorical):
    graph_spec = make_graph_spec(data_loader_categorical)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_categorical)
    inference_model = exporter.get_inference_model()

    x = {"x1": np.array(["cat", "dog", "house"])}
    y = inference_model(x)

    for prediction in y["y1"].numpy():  # Loop over each prediction in batch
        assert prediction in [b"animal", b"non-animal"]


def test_inference_takes_matrix_input(script_factory, data_loader_image):
    graph_spec = make_graph_spec(data_loader_image)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader_image)
    inference_model = exporter.get_inference_model()

    x = {"x1": np.random.random((5, 16, 16, 3))}
    y = inference_model(x)

    for prediction in y["y1"].numpy():  # Loop over each prediction in batch
        assert prediction in [b"animal", b"non-animal"]


def test_export_fastapi_files_are_present(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    on_exported = MagicMock()
    exporter = Exporter(
        graph_spec, training_model, data_loader, on_model_exported=on_exported
    )

    expected_files = {
        "saved_model.pb",
        "keras_metadata.pb",
        "assets",
        "variables",
        join_and_sanitize("variables", "variables.index"),
        join_and_sanitize("variables", "variables.data-00000-of-00001"),
        fastapi_utils.SCRIPT_FILE,
        fastapi_utils.REQUIREMENTS_FILE,
        fastapi_utils.EXAMPLE_REQUIREMENTS_FILE,
        fastapi_utils.EXAMPLE_JSON_FILE,
        fastapi_utils.EXAMPLE_SCRIPT_FILE,
        fastapi_utils.EXAMPLE_CSV_FILE,
    }

    target_dir = join_and_sanitize(temp_path, "export_model")
    assert not os.path.isdir(target_dir)

    actual_files = set(exporter.export(target_dir, mode="FastAPI"))

    assert actual_files == expected_files
    assert all(os.path.exists(join_and_sanitize(target_dir, p)) for p in expected_files)
    assert on_exported.call_count == 1


def test_export_fastapi_endpoint_healthy(script_factory, data_loader, temp_path):
    graph_spec = make_graph_spec(data_loader)
    training_model = TrainingModel(script_factory, graph_spec)
    exporter = Exporter(graph_spec, training_model, data_loader)
    exporter.export(temp_path, mode="FastAPI")

    module = module_from_path(join_and_sanitize(temp_path, fastapi_utils.SCRIPT_FILE))

    app = module.create_app()
    client = TestClient(app)

    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == {"healthy": True}


@pytest.mark.parametrize("data", [data0, data1, data2, data3])
def test_export_fastapi_endpoint_predict(data, script_factory, temp_path):
    with make_data_loader(data) as data_loader:
        graph_spec = make_graph_spec(data_loader)
        training_model = TrainingModel(script_factory, graph_spec)
        exporter = Exporter(graph_spec, training_model, data_loader)
        exporter.export(temp_path, mode="FastAPI")

        module = module_from_path(
            join_and_sanitize(temp_path, fastapi_utils.SCRIPT_FILE)
        )
        app = module.create_app()
        client = TestClient(app)

        def make_payload(dict_):
            payload = {}
            for feature, tensor in dict_.items():

                def f(x):
                    if isinstance(x, bytes):
                        x = x.decode()
                    return x

                payload[feature] = [f(x) for x in tensor.numpy().tolist()]
            return payload

        inference_model = exporter.get_inference_model()
        for batch_size in [1, 3]:
            x, _ = data_loader.get_example_batch(
                batch_size=batch_size, apply_pipelines="loader"
            )
            y_expected = make_payload(inference_model(x))

            response = client.post("/predict", json=make_payload(x))
            y_actual = response.json()

            assert response.status_code == 200
            assert y_actual == y_expected


@pytest.mark.parametrize("data", [data0, data1, data2, data3])
def test_export_fastapi_endpoint_predict_using_example_script(
    data, script_factory, temp_path
):
    with make_data_loader(data) as data_loader:
        graph_spec = make_graph_spec(data_loader)
        training_model = TrainingModel(script_factory, graph_spec)
        exporter = Exporter(graph_spec, training_model, data_loader)
        exporter.export(temp_path, mode="FastAPI")

        server_module = module_from_path(
            join_and_sanitize(temp_path, fastapi_utils.SCRIPT_FILE)
        )
        app = server_module.create_app()
        client = TestClient(app)

        example_module = module_from_path(
            join_and_sanitize(temp_path, fastapi_utils.EXAMPLE_SCRIPT_FILE)
        )
        data = example_module.make_payload()
        response = client.post("/predict", json=data).json()

        batch_size = len(
            next(iter(data.values()))
        )  #  length of arbitrary feature vector
        _, targets = data_loader.get_example_batch(
            batch_size=batch_size, apply_pipelines="loader"
        )

        for feature_name in response.keys():
            assert np.shape(response[feature_name]) == np.shape(targets[feature_name])
