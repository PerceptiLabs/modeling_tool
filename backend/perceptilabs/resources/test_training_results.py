import os
import pytest
from unittest.mock import MagicMock

from perceptilabs.resources.training_results import TrainingResultsAccess
from perceptilabs.rygg import RyggAdapter


class Rygg(RyggAdapter):
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path

    def get_dataset(self, call_context, dataset_id):
        raise NotImplementedError

    def create_model(
        self, call_context, project_id, dataset_id, model_name, location=None
    ):
        raise NotImplementedError

    def load_model_json(self, call_context, model_id):
        raise NotImplementedError

    def save_model_json(self, call_context, model_id, model):
        raise NotImplementedError

    def get_model(self, call_context, model_id):
        return {"location": "/tmp"}


def test_store_and_get_latest(tmp_path):
    rygg = Rygg(tmp_path)
    access = TrainingResultsAccess(rygg)

    expected_results = {"abc": "123"}
    access.store({}, "session-id", expected_results)

    actual_results = access.get_latest({}, "session-id")
    assert actual_results == expected_results


def test_remove(tmp_path):
    rygg = Rygg(tmp_path)
    access = TrainingResultsAccess(rygg)

    results = {"abc": "123"}
    access.store({}, "session-id", results)
    access.remove({}, "session-id")

    actual_results = access.get_latest({}, "session-id")
    assert actual_results is None


def test_remove_raises_error_on_fail(monkeypatch, tmp_path):
    rygg = Rygg(tmp_path)
    access = TrainingResultsAccess(rygg)
    access.store({}, "123", {"abc": "123"})  # Store some results

    # Prevent removing the existing result file
    fake_remove = MagicMock()
    fake_remove.side_effect = PermissionError("Not allowed to delete this file!")
    monkeypatch.setattr(os, "remove", fake_remove)

    with pytest.raises(PermissionError):
        access.remove({}, "123")


def test_remove_retries_at_least_once(monkeypatch, tmp_path):
    rygg = Rygg(tmp_path)
    access = TrainingResultsAccess(rygg)
    access.store({}, "session-id", {"abc": "123"})  # Store some results

    real_remove = os.remove

    attempts = 0

    def fake_remove(path):
        nonlocal attempts

        try:
            if attempts == 0:
                raise PermissionError("Not allowed to delete this file!")
            else:
                real_remove(path)
        except:
            raise
        finally:
            attempts += 1

    monkeypatch.setattr(os, "remove", fake_remove)
    access.remove({}, "session-id")

    actual_results = access.get_latest({}, "session-id")
    assert actual_results is None
