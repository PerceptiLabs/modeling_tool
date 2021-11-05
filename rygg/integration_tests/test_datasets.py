import glob
import os
import pytest
import shutil

from clients import DatasetClient, ModelClient
from assertions import (
    assert_dict_lists_equal, \
    has_expected_files, \
    assert_eventually, \
)

SMALL_DATASET_SIZE = 10 * 1024 ** 2 # 10 MB
LARGE_DATASET_SIZE = 100 * 1024 ** 2 # 100 MB

def assert_workingdir(rest, project_id):
    if rest.is_enterprise:
        assert os.path.isdir(rest.get_upload_dir(project_id))


def assert_task_starts(rest, task):
    def progress_is_midway():
        try:
            task.refresh()
            return task.is_started
        except Exception as e:
            raise e

    # poll frequently to try to catch it in the midway state
    assert_eventually(progress_is_midway, stop_max_delay=5000, wait_fixed=50)

def assert_task_progresses(rest, task):
    def progress_is_midway():
        try:
            task.refresh()
            return task.so_far > 0
        except Exception as e:
            raise e

    # poll frequently to try to catch it in the midway state
    assert_eventually(progress_is_midway, stop_max_delay=60000, wait_fixed=1000)

def assert_task_completes(rest, task):
    def state_is_completed():
        task.refresh()
        ret = task.is_completed
        return ret

    assert_eventually(state_is_completed, stop_max_delay=10000, wait_fixed=1000)


@pytest.mark.timeout(1)
def test_deleting_model_removes_it_from_dataset_models_list(rest, tmp_project, tmp_dataset):
    assert not tmp_dataset.models
    with ModelClient.make(rest, project=tmp_project.id, name="model") as model:
        assert not tmp_dataset.models

        tmp_dataset.add_models([model.id])
        assert len(tmp_dataset.models) == 1

    # with the model deleted, it should just vanish from the dataset
    assert not tmp_dataset.models


@pytest.mark.timeout(5)
def test_delete_dataset_in_downloading(rest, tmpdir, tmp_project):
    if rest.is_enterprise:
        dest = rest.get_upload_dir(tmp_project.id)
    else:
        dest = tmpdir


    # make a remote dataset from a medium dataset
    medium_dataset_name = get_medium_remote_record(rest)["UniqueName"]
    glob_pattern = os.path.join(dest, medium_dataset_name)
    def is_zip_removed():
        found_files = glob.glob(glob_pattern, recursive=True)
        return not found_files


    task, dataset = DatasetClient.create_from_remote(rest, tmp_project, medium_dataset_name, tmpdir)

    with task:
        with dataset:

            # wait for it to start unzipping
            assert_task_starts(rest, task)

            # cancel the download by leaving the context and deleting the dataset



        # Make sure the dataset is gone
        assert not dataset.exists

        # make sure the destination directory and zip is deleted
        # Make sure the zip is deleted
        assert_eventually(is_zip_removed, stop_max_delay=10000, wait_fixed=100)

@pytest.mark.timeout(15)
def test_cancel_download_task(rest, tmpdir, tmp_project):
    if rest.is_enterprise:
        dest = rest.get_upload_dir(tmp_project.id)
    else:
        dest = tmpdir

    # make a remote dataset from a large dataset
    medium_dataset_name = get_medium_remote_record(rest)["UniqueName"]
    glob_pattern = os.path.join(dest, medium_dataset_name)
    def is_zip_removed():
        found_files = glob.glob(glob_pattern, recursive=True)
        return not found_files

    # find a large dataset
    big_dataaset_name = get_large_remote_record(rest)['UniqueName']

    # create a large dataset from remote
    task, dataset = DatasetClient.create_from_remote(rest, tmp_project, big_dataaset_name, tmpdir)
    try:
        with task:
            # Cancel it while it's downloading
            assert_task_starts(rest, task)
            assert_task_progresses(rest, task)
    finally:
        # wait for the task to go away so we don't starve subsequent tests
        assert_eventually(lambda: not task.exists or task.is_completed, stop_max_delay=2000, wait_fixed=100)

    # watch to see the dataset deleted
    assert_eventually(lambda: not dataset.exists, stop_max_delay=2000, wait_fixed=100)

    # Make sure the zip is deleted
    assert_eventually(is_zip_removed, stop_max_delay=10000, wait_fixed=100)

    # try to create a new dataset from the same remote. It should succeed
    task, dataset = DatasetClient.create_from_remote(rest, tmp_project, big_dataaset_name, tmpdir)

    try:
        with task, dataset:
            pass
    finally:
        # wait for the task to go away so we don't starve subsequent tests
        assert_eventually(lambda: not task.exists or task.is_completed, stop_max_delay=2000, wait_fixed=100)


@pytest.mark.timeout(5)
@pytest.mark.usefixtures('enterprise_only')
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
@pytest.mark.usefixtures('enterprise_only')
def test_dataset_rejects_slash_local(tmp_project, rest):
    with pytest.raises(Exception, match="400.*char"):
        DatasetClient.make(rest, name="slash file", location="a_name_with/a_slash", project=tmp_project.id)


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('pip_only')
def test_local_dataset_is_already_uploaded(rest, tmp_text_file, tmp_dataset):
    # For local, the dataset is already uploaded
    assert tmp_dataset.status == "uploaded"


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
def test_that_upload_sets_dataset_completed(rest, tmp_text_file, tmp_dataset):
    filename = os.path.basename(tmp_text_file)
    ret=rest.post_file("/upload", tmp_text_file, tmp_dataset.location, dataset_id=tmp_dataset.id, project_id=tmp_dataset.project)
    tmp_dataset.refresh()
    assert tmp_dataset.status == "uploaded"

    # Just for kicks, check that the upload worked
    assert has_expected_files(rest, tmp_dataset.project, [filename], None)

    # make sure we didn't delete too high in the directory tree
    assert_workingdir(rest, tmp_dataset.project)


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('pip_only')
def test_new_dataset_round_trips_fields_local(rest, tmp_project, tmp_model, tmp_text_file):
    name = f"data with {tmp_text_file}"
    with DatasetClient.make(rest, name=name, location=tmp_text_file, project=tmp_project.id, models=[tmp_model.id]) as dataset:

        refetched = DatasetClient(rest, dataset.id)
        # test that creating a dataset returns one that's waiting for an upload
        assert refetched.status == "uploaded"
        assert refetched.name == name
        assert refetched.location == tmp_text_file
        assert refetched.models == [tmp_model.as_dict]

@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
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


# #We can't actually support deleting datasets from uploads because we don't have the directory, just the csv
# @pytest.mark.timeout(5)
# @pytest.mark.usefixtures('enterprise_only')
# def test_deleting_dataset_deletes_file(rest, tmp_text_file, tmp_project):
#     filename = os.path.basename(tmp_text_file)
#     expected_upload_dest = os.path.join(rest.get_upload_dir(tmp_project.id), filename)
#     name = f"data with {filename}"
#
#     with DatasetClient.make(rest, name=name, location=filename, project=tmp_project.id) as dataset:
#         rest.post_file("/upload", tmp_text_file, dataset.location, dataset_id=dataset.id)
#
#         dataset_id = dataset.id
#
#         # Just for kicks, check that the upload worked
#         assert has_expected_files(rest, [filename], None)
#         assert os.path.exists(expected_upload_dest)
#
#     # leaving the with block will remove the dataset
#     def dataset_is_removed():
#         try:
#             rest.get(f"/datasets/{dataset_id}")
#             return False
#         except:
#             return True
#
#     assert_eventually(dataset_is_removed, stop_max_delay=5000, wait_fixed=50)
#
#     def path_is_removed():
#         ret = os.path.exists(expected_upload_dest)
#         return not ret
#
#     # Local rygg won't delete the files
#     if rest.is_enterprise:
#         assert_eventually(path_is_removed, stop_max_delay=5000, wait_fixed=50)
#
#     # make sure we didn't delete too high in the directory tree
#     assert_workingdir(rest)


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
def test_cant_upload_to_filename_that_doesnt_match_dataset(rest, tmp_text_file, tmp_dataset):
    filename = os.path.basename(tmp_text_file)
    with pytest.raises(Exception, match="400.*location"):
        rest.post_file("/upload", tmp_text_file, tmp_dataset.location+"_WRONG", tmp_dataset.project, dataset_id=tmp_dataset.id)


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


def get_small_remote_record(rest):
    for dataset,sz in get_available_remote_datasets(rest):
        if sz <= SMALL_DATASET_SIZE:
            return dataset
    return None


def get_medium_remote_record(rest):
    # find a dataset between SMALL_DATASET_SIZE and LARGE_DATASET_SIZE
    for dataset,sz in get_available_remote_datasets(rest):
        if sz <= LARGE_DATASET_SIZE and sz >= SMALL_DATASET_SIZE:
            return dataset
    return None


def get_large_remote_record(rest):
    # find a dataset between SMALL_DATASET_SIZE and LARGE_DATASET_SIZE
    for dataset,sz in get_available_remote_datasets(rest):
        if sz >= LARGE_DATASET_SIZE:
            return dataset
    return None


def get_available_remote_datasets(rest):
    resp = rest.get("/datasets/remote_with_categories")

    for dataset in resp["datasets"]:
        if not "SizeBytes" in dataset:
            continue
        sz = int(dataset["SizeBytes"])
        yield (dataset, sz)


@pytest.mark.timeout(1)
def test_deleting_allows_same_name(rest, tmpdir, tmp_project):
    assert os.path.isdir(tmpdir)

    # make a fake file
    if rest.is_enterprise:
        filename = "loc1"
    else:
        filename = os.path.join(tmpdir, "f")
        open(filename, "w").write("text")
        assert os.path.isfile(filename)

    common_params = {
        "project": tmp_project.id,
        "location": filename,
        "name": "dataset"
    }

    # create and then delete a dataset
    ds = DatasetClient.make(rest, **common_params)

    # now try to make another with the same name and location
    with pytest.raises(Exception, match="400"):
        DatasetClient.make(rest, **common_params)

    # delete the original dataset to make room
    ds.delete()

    # now we should be able to make a duplicate
    DatasetClient.make(rest, **common_params)


@pytest.mark.timeout(10)
def test_create_dataset_from_remote(rest, tmpdir, tmp_project):
    # don't try this if the remote dataset is already linked to the dataset, which means that we're working on a non-test system
    test_record = get_small_remote_record(rest)
    assert test_record

    task, dataset = DatasetClient.create_from_remote(rest, tmp_project, test_record["UniqueName"], tmpdir)

    # make sure the task acts as expected
    assert_task_starts(rest, task)
    assert_task_completes(rest, task)

    # re-fetch the dataset by id
    assert dataset.status == "uploaded"
    assert dataset.is_perceptilabs_sourced == True

    # Check the download. Since we currently only support csv, make sure it's the right file type
    assert os.path.isfile(dataset.location)
    assert dataset.location.endswith(".csv")
    content = rest.get('/files/get_file_content', path=dataset.location, project_id=tmp_project.id)['file_contents']
    assert len(content) > 0
    assert "," in content[0] # very rudimentary check that it's csv

    # check that the zip has been deleted
    if rest.is_enterprise:
        parent_dir = dataset.location
        full_parent_dir = os.path.join(rest.get_upload_dir(tmp_project.id), parent_dir)
    else:
        full_parent_dir = dataset.location
    assert not glob.glob(os.path.join(full_parent_dir, "**/*.zip"))

    # also try fetching the list
    datasets = rest.get(f"/datasets/")
    assert datasets['count'] == 1
    filtered = filter(lambda d: d['dataset_id'] == dataset.id, datasets['results'])
    as_list = list(filtered)
    assert len(as_list) == 1
    assert as_list[0]['exists_on_disk'] == True

    # Check that the new dataset points to the remote dataset
    source_url = dataset.source_url
    remote_url_ending = test_record["UniqueName"]
    assert source_url.endswith(remote_url_ending)

    # re-fetch the remotes list so we can check the localDatasetId
    remotes = [d for d in rest.get('/datasets/remote/') if d['UniqueName'] == test_record['UniqueName']]
    assert remotes
    test_record = remotes[0]

    # check that remote datasets response now points to the new dataset
    for remote,_ in get_available_remote_datasets(rest):
        if remote["UniqueName"] == test_record["UniqueName"]:
            assert test_record["localDatasetID"] == dataset.id
            break

    # check that deleting the local copy makes exists_on_disk change to false
    assert dataset.exists_on_disk == True
    shutil.rmtree(os.path.dirname(dataset.location), ignore_errors=True)
    dataset.refresh()
    assert dataset.exists_on_disk == False

    # make sure we didn't delete too high in the directory tree
    assert_workingdir(rest, tmp_project.id)
