import os
from zipfile import ZipFile
from perceptilabs.resources.model_archives import ModelArchivesAccess


def test_model_json_always_included(tmp_path):
    path = os.path.join(tmp_path, 'my_archive.zip')
    
    access = ModelArchivesAccess()
    access.write(path)
    
    with ZipFile(path, 'r') as archive:
        assert 'model.json' in archive.namelist()

