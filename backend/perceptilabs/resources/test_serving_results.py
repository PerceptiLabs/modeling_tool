import os
import pytest
from unittest.mock import MagicMock

from perceptilabs.resources.serving_results import ServingResultsAccess
from perceptilabs.rygg import RyggAdapter


class Rygg(RyggAdapter):
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path

    def get_dataset(self, dataset_id):
        raise NotImplementedError

    def create_model(self, project_id, dataset_id, model_name, location=None):
        raise NotImplementedError

    def load_model_json(self, model_id):
        raise NotImplementedError

    def save_model_json(self, model_id, model):
        raise NotImplementedError

    def get_model(self, call_context, model_id):
        return {'location': '/tmp'}

    
def test_store_and_get_latest(tmp_path):
    rygg = Rygg(tmp_path)
    access = ServingResultsAccess(rygg)

    session_id = access.new_id(call_context={}, model_id='300')
    
    expected_results = {'abc': '123'}
    access.store(session_id, expected_results)

    actual_results = access.get_latest(session_id)
    assert actual_results == expected_results


def test_store_and_remove(tmp_path):
    rygg = Rygg(tmp_path)
    access = ServingResultsAccess(rygg)
    session_id = access.new_id(call_context={}, model_id='300')
    
    results = {'abc': '123'}
    access.store(session_id, results)

    assert access.get_latest(session_id) is not None

    serving_dir = access.get_serving_directory(session_id) 
    assert serving_dir is not None
    assert os.path.isdir(serving_dir)

    results = {'abc': '123'}
    access.remove(session_id)
    assert access.get_latest(session_id) is None
    assert not os.path.isdir(serving_dir)    

