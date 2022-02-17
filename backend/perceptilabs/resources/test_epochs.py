import os
import pytest
from unittest.mock import MagicMock
from perceptilabs.resources.epochs import EpochsAccess


@pytest.fixture(scope='function')
def access(monkeypatch, tmp_path):
    rygg = MagicMock()
    rygg.get_model.return_value = {'location': tmp_path}
    access = EpochsAccess(rygg)

    files = {
        'state-0009.pkl': 9,
        'checkpoint-0009.ckpt.index': 9,
        'state-0010.pkl': 10,
        'checkpoint-0010.ckpt.index': 10,
        'state-0100.pkl': 100,
        'checkpoint-0200.ckpt.index': 200,
    }

    def fake_listdir(directory):
        yield from files.keys()

    def fake_getmtime(file_path):
        file_name = os.path.basename(file_path)
        return files[file_name]

    monkeypatch.setattr(os, 'listdir', fake_listdir)
    monkeypatch.setattr(os.path, 'getmtime', fake_getmtime)
    return access


@pytest.fixture()
def training_session_id(temp_path):
    return '123'


def test_get_latest_require_checkpoint(access, training_session_id):
    epoch_id = access.get_latest({}, training_session_id, require_checkpoint=True, require_trainer_state=False)
    assert epoch_id == 200


def test_get_latest_require_state(access, training_session_id):
    epoch_id = access.get_latest({}, training_session_id, require_checkpoint=False, require_trainer_state=True)
    assert epoch_id == 100


def test_get_latest_require_both(access, training_session_id):
    epoch_id = access.get_latest({}, training_session_id, require_checkpoint=True, require_trainer_state=True)
    assert epoch_id == 10

