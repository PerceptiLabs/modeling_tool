import os
import pytest
import shutil

from clients import DatasetClient, ModelClient
from assertions import (
    assert_dict_lists_equal, \
    has_expected_files, \
    assert_eventually, \
)

MAX_DATASET_SIZE = 10 * 1024 * 1024 # 10 MB

@pytest.mark.timeout(1)
def test_deleting_model_removes_it_from_dataset_models_list(rest, tmp_project, tmp_dataset):
    assert not tmp_dataset.models
    with ModelClient.make(rest, project=tmp_project.id, name="model") as model:
        assert not tmp_dataset.models

        tmp_dataset.add_models([model.id])
        assert len(tmp_dataset.models) == 1

    # with the model deleted, it should just vanish from the dataset
    assert not tmp_dataset.models


@pytest.mark.timeout(1)
def test_dataset_model_association_after_create(rest, tmp_project, tmp_model):
    if not rest.is_enterprise():
        return

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


@pytest.mark.timeout(1)
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


@pytest.mark.timeout(1)
def test_dataset_rejects_slash(tmp_project, rest):
    if not rest.is_enterprise():
        return

    with pytest.raises(Exception, match="400.*char"):
        DatasetClient.make(rest, name="slash file", location="a_name_with/a_slash", project=tmp_project.id)


@pytest.mark.timeout(1)
def test_that_upload_sets_dataset_completed(rest, tmp_text_file, tmp_dataset):
    # For local, the dataset is already uploaded
    if not rest.is_enterprise():
        assert tmp_dataset.status == "uploaded"
        return

    filename = os.path.basename(tmp_text_file)
    ret=rest.post_file("/upload", tmp_text_file, tmp_dataset.location, dataset_id=tmp_dataset.id)
    tmp_dataset.refresh()
    assert tmp_dataset.status == "uploaded"

    # Just for kicks, check that the upload worked
    assert has_expected_files(rest, [filename], None)


@pytest.mark.timeout(1)
def test_new_dataset_round_trips_fields(rest, tmp_project, tmp_model, tmp_text_file):
    if rest.is_enterprise():
        filename = os.path.basename(tmp_text_file)
        expected_status = "new"
    else:
        filename = tmp_text_file
        expected_status = "uploaded"

    name = f"data with {filename}"
    with DatasetClient.make(rest, name=name, location=filename, project=tmp_project.id, models=[tmp_model.id]) as dataset:

        refetched = DatasetClient(rest, dataset.id)
        # test that creating a dataset returns one that's waiting for an upload
        assert refetched.status == expected_status
        assert refetched.name == name
        assert refetched.location == filename
        assert refetched.models == [tmp_model.as_dict]


@pytest.mark.timeout(5)
def test_deleting_dataset_deletes_file(rest, tmp_text_file, tmp_project):
    if not rest.is_enterprise():
        return

    upload_path = rest.get("/upload_dir")["path"]
    filename = os.path.basename(tmp_text_file)
    expected_upload_dest = os.path.join(upload_path, filename)
    name = f"data with {filename}"

    with DatasetClient.make(rest, name=name, location=filename, project=tmp_project.id) as dataset:
        rest.post_file("/upload", tmp_text_file, dataset.location, dataset_id=dataset.id)

        dataset_id = dataset.id

        # Just for kicks, check that the upload worked
        assert has_expected_files(rest, [filename], None)
        assert os.path.exists(expected_upload_dest)

    # leaving the with block will remove the dataset
    def dataset_is_removed():
        try:
            rest.get(f"/datasets/{dataset_id}")
            return False
        except:
            return True

    assert_eventually(dataset_is_removed, stop_max_delay=5000, wait_fixed=50)

    def path_is_removed():
        ret = os.path.exists(expected_upload_dest)
        return not ret

    # Local rygg won't delete the files
    if rest.is_enterprise():
        assert_eventually(path_is_removed, stop_max_delay=5000, wait_fixed=50)


@pytest.mark.timeout(1)
def test_cant_upload_to_filename_that_doesnt_match_dataset(rest, tmp_text_file, tmp_dataset):
    if not rest.is_enterprise():
        return

    filename = os.path.basename(tmp_text_file)
    with pytest.raises(Exception, match="400.*location"):
        rest.post_file("/upload", tmp_text_file, tmp_dataset.location+"_WRONG", dataset_id=tmp_dataset.id)


@pytest.mark.timeout(1)
def test_remote_categories(rest):
    response = rest.get("/datasets/remote_categories")
    assert "kaggle" in response


@pytest.mark.timeout(1)
def test_remote_list(rest):
    response = rest.get("/datasets/remote_with_categories")
    assert len(response["datasets"]) >= 1
    key_set = response["datasets"][0].keys()
    assert "UniqueName" in key_set


@pytest.mark.timeout(1)
def get_remote_record(rest):
    resp = rest.get("/datasets/remote_with_categories")

    # find a dataset under MAX_DATASET_SIZE
    for dataset in resp["datasets"]:
        if not "SizeBytes" in dataset:
            continue
        sz = int(dataset["SizeBytes"])
        if sz <= MAX_DATASET_SIZE:
            return dataset
    return None


def assert_task_progresses(rest, task_id):
    def progress_is_midway():
        resp = rest.get(f"/tasks/{task_id}/")
        assert resp
        return resp.get("state") == "STARTED" \
                and resp.get("so_far") > 1

    def state_is_completed():
        resp = rest.get(f"/tasks/{task_id}/")
        assert resp
        return resp.get("state") == "SUCCESS" \
                and resp.get("so_far") == resp.get("expected")

    if os.getenv("USER"):
        # poll frequently to try to catch it in the midway state
        assert_eventually(progress_is_midway, stop_max_delay=10000, wait_fixed=50)

    assert_eventually(state_is_completed, stop_max_delay=10000, wait_fixed=1000)


@pytest.mark.timeout(10)
def test_create_dataset_from_remote(rest, tmpdir, tmp_project):
    # don't try this if the remote dataset is already linked to the dataset, which means that we're working on a non-test system
    test_record = get_remote_record(rest)
    assert test_record


    resp = rest.post('/datasets/create_from_remote/', {}, id=test_record["UniqueName"], destination=tmpdir, project_id=tmp_project.id)
    assert "task_id" in resp
    assert "dataset_id" in resp

    task_id = resp["task_id"]
    dataset_id = resp["dataset_id"]

    assert_task_progresses(rest, task_id)

    # re-fetch the dataset by id
    dataset = rest.get(f"/datasets/{dataset_id}/")
    assert dataset

    # also try fetching the list
    datasets = rest.get(f"/datasets/")
    assert datasets['count'] == 1
    filtered = filter(lambda d: d['dataset_id'] == dataset['dataset_id'], datasets['results'])
    as_list = list(filtered)
    assert len(as_list) == 1
    dataset = as_list[0]
    assert dataset['exists_on_disk'] == True

    # Check that the new dataset points to the remote dataset
    source_url = dataset["source_url"]
    remote_url_ending = test_record["UniqueName"]
    assert source_url.endswith(remote_url_ending)

    # check that remote datasets response now points to the new dataset
    test_record = get_remote_record(rest)
    assert test_record["localDatasetID"] == dataset_id

    # check that deleting the local copy makes exists_on_disk change to false
    shutil.rmtree(dataset['location'], ignore_errors=True)
    dataset = rest.get(f"/datasets/{dataset_id}/")
    assert dataset['exists_on_disk'] == False

    # TODO check the download
