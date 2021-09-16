import os
import pytest

from clients import DatasetClient, ModelClient
from assertions import (
    assert_dict_lists_equal, \
    has_expected_files, \
    assert_eventually, \
)

def test_deleting_model_removes_it_from_dataset_models_list(rest, tmp_project, tmp_dataset):
    assert not tmp_dataset.models
    with ModelClient.make(rest, project=tmp_project.id, name="model") as model:
        assert not tmp_dataset.models

        tmp_dataset.add_models([model.id])
        assert len(tmp_dataset.models) == 1

    # with the model deleted, it should just vanish from the dataset
    assert not tmp_dataset.models


def test_dataset_model_association_after_create(rest, tmp_project, tmp_model):
    with DatasetClient.make(rest, project=tmp_project.id, location="loc1", name="dataset1") as dataset1, \
         DatasetClient.make(rest, project=tmp_project.id, location="loc2", name="dataset2") as dataset2:

        tmp_model.update(datasets = [dataset1.id])
        assert tmp_model.datasets == [dataset1.as_dict]

        # update datasets replaces the whole list
        tmp_model.update(datasets = [dataset2.id])
        assert_dict_lists_equal(tmp_model.datasets, [dataset2.as_dict], "dataset_id")

        # add_datasets adds to them
        tmp_model.add_datasets([dataset1.id])
        assert_dict_lists_equal(tmp_model.datasets, [dataset1.as_dict, dataset2.as_dict], "dataset_id")

        # show that we can delete the association
        tmp_model.remove_datasets([dataset1.id, dataset2.id])
        assert len(tmp_model.datasets) == 0

def test_model_dataset_association_after_create(rest, tmp_project, tmp_dataset):
    with ModelClient.make(rest, project=tmp_project.id, name="model1") as model1, \
         ModelClient.make(rest, project=tmp_project.id, name="model2") as model2:

        tmp_dataset.update(models = [model1.id])
        assert tmp_dataset.models == [model1.as_dict]

        # update models replaces the whole list
        tmp_dataset.update(models = [model2.id])
        assert_dict_lists_equal(tmp_dataset.models, [model2.as_dict], "model_id")

        # add_models adds to them
        tmp_dataset.add_models([model1.id])
        assert_dict_lists_equal(tmp_dataset.models, [model1.as_dict, model2.as_dict], "model_id")

        # show that we can delete the association
        tmp_dataset.remove_models([model1.id, model2.id])
        assert len(tmp_dataset.models) == 0

def test_dataset_rejects_slash(tmp_project, rest):
    with pytest.raises(Exception, match="400.*char"):
        DatasetClient.make(rest, name="slash file", location="a_name_with/a_slash", project=tmp_project.id)

def test_that_upload_sets_dataset_completed(rest, tmp_text_file, tmp_dataset):
    filename = os.path.basename(tmp_text_file)
    ret=rest.post_file("/upload", tmp_text_file, tmp_dataset.location, dataset_id=tmp_dataset.id)
    tmp_dataset.refresh()
    assert tmp_dataset.status == "uploaded"

    # Just for kicks, check that the upload worked
    assert has_expected_files(rest, [filename])

def test_new_dataset_round_trips_fields(rest, tmp_project, tmp_model, tmp_text_file):
    filename = os.path.basename(tmp_text_file)
    name = f"data with {filename}"
    with DatasetClient.make(rest, name=name, location=filename, project=tmp_project.id, models=[tmp_model.id]) as dataset:

        refetched = DatasetClient(rest, dataset.id)
        # test that creating a dataset returns one that's waiting for an upload
        assert refetched.status == "new"
        assert refetched.name == name
        assert refetched.location == filename
        assert refetched.models == [tmp_model.as_dict]

def test_deleting_dataset_deletes_file(rest, tmp_text_file, tmp_project):
    filename = os.path.basename(tmp_text_file)
    name = f"data with {filename}"

    with DatasetClient.make(rest, name=name, location=filename, project=tmp_project.id) as dataset:
        ret = rest.post_file("/upload", tmp_text_file, dataset.location, dataset_id=dataset.id)

        # Just for kicks, check that the upload worked
        assert has_expected_files(rest, [filename])

    def path_is_removed():
        not os.path.isfile(expected_dest)

    assert_eventually(path_is_removed, stop_max_delay=10000, wait_fixed=1000)

def test_cant_upload_to_filename_that_doesnt_match_dataset(rest, tmp_text_file, tmp_dataset):
    filename = os.path.basename(tmp_text_file)
    with pytest.raises(Exception, match="400.*location"):
        rest.post_file("/upload", tmp_text_file, tmp_dataset.location+"_WRONG", dataset_id=tmp_dataset.id)
