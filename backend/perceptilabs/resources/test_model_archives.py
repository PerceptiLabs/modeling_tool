import os
import numpy as np
from zipfile import ZipFile
from perceptilabs.resources.model_archives import ModelArchivesAccess


def test_model_json_always_included(tmp_path):
    path = os.path.join(tmp_path, 'my_archive.zip')
    
    access = ModelArchivesAccess()
    access.write(path)
    
    with ZipFile(path, 'r') as archive:
        assert 'model.json' in archive.namelist()


def test_extra_paths_are_included(tmp_path):
    archive_path = os.path.join(tmp_path, 'my_archive.zip')

    expected_data = np.random.random((25, 25))
    numpy_path = os.path.join(tmp_path, 'data.npy')
    np.save(numpy_path, expected_data)
    
    
    access = ModelArchivesAccess()
    access.write(
        archive_path,
        extra_paths={numpy_path: None},
    )
    
    with ZipFile(archive_path, 'r') as archive:
        assert 'model.json' in archive.namelist()
        assert 'data.npy' in archive.namelist()

        with archive.open('data.npy') as data_file:
            actual_data = np.load(data_file)
            assert (actual_data == expected_data).all()
            

def test_extra_paths_can_be_remapped(tmp_path):
    archive_path = os.path.join(tmp_path, 'my_archive.zip')
    
    expected_data = np.random.random((25, 25))
    numpy_path = os.path.join(tmp_path, 'data.npy')
    np.save(numpy_path, expected_data)

    access = ModelArchivesAccess()
    access.write(
        archive_path,
        extra_paths={numpy_path: 'renamed_data.npy'},
    )
    
    with ZipFile(archive_path, 'r') as archive:
        assert 'model.json' in archive.namelist()
        assert 'data.npy' not in archive.namelist()
        assert 'renamed_data.npy' in archive.namelist()        

        with archive.open('renamed_data.npy') as data_file:
            actual_data = np.load(data_file)
            assert (actual_data == expected_data).all()

        
