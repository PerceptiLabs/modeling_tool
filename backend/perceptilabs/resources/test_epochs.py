import os
import pytest
from perceptilabs.resources.epochs import EpochsAccess


@pytest.fixture(scope='function')
def access(monkeypatch):
    access = EpochsAccess()

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


def test_get_latest_require_checkpoint(access, temp_path):
    epoch_id = access.get_latest(temp_path, require_checkpoint=True, require_trainer_state=False)
    assert epoch_id == 200

    
def test_get_latest_require_state(access, temp_path):
    epoch_id = access.get_latest(temp_path, require_checkpoint=False, require_trainer_state=True)
    assert epoch_id == 100

    
def test_get_latest_require_both(access, temp_path):
    epoch_id = access.get_latest(temp_path, require_checkpoint=True, require_trainer_state=True)
    assert epoch_id == 10


    




