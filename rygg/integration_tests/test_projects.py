import os
import pytest
import time

from rest import RyggRest
from clients import ProjectClient, ModelClient, NotebookClient, DatasetClient
from assertions import assert_eventually

@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
def test_project_creates_and_deletes_dir(rest):
    # create project
    with ProjectClient.make(rest, name="test project") as project:
        project_id = project.id

        project_dir = rest.get_upload_dir(project_id)
        assert os.path.isdir(project_dir)

    assert_eventually(lambda: not os.path.isdir(project_dir), stop_max_delay=2000, wait_fixed=100)


def test_project_delete(rest):
    with ProjectClient.make(rest, name="test project") as project:
        pass

    assert not project.exists


def test_project_delete_also_deletes_model(rest):
    with ProjectClient.make(rest, name="test project") as project:
        model = ModelClient.make(rest, project=project.id, name="model name")

    assert not model.exists


def test_project_delete_also_deletes_dataset(rest, tmp_text_file):
    if rest.is_enterprise:
        filename = os.path.basename(tmp_text_file)
    else:
        filename = tmp_text_file

    with ProjectClient.make(rest, name="test project") as project:
        dataset = DatasetClient.make(rest, name="some file", location=filename, project=project.id, models=[])

    assert not dataset.exists


def test_project_delete_also_deletes_notebook(rest):
    with ProjectClient.make(rest, name="test project") as project:
        notebook = NotebookClient.make(rest, project=project.id, name="notebook1")

    assert not notebook.exists


def test_notebook_project_link(rest, tmp_project):
    with NotebookClient.make(rest, project=tmp_project.id, name="notebook1") as notebook:
        tmp_project.refresh()
        assert notebook.id in [n["notebook_id"] for n in tmp_project.notebooks]


def test_model_project_link(rest, tmp_project):
    with ModelClient.make(rest, project=tmp_project.id, name="model name") as model:
        assert model.name == "model name"
        assert model.project == tmp_project.id
        tmp_project.refresh()
        assert tmp_project.models == [model.id]


def test_project_update(tmp_project):
    time.sleep(0.1)  # just enough to put a gap between create and update date
    tmp_project.update(name="this is a new name")

    assert tmp_project.updated > tmp_project.created
    assert tmp_project.name == "this is a new name"

# TODO: this will be reenabled when we don't use project_id as the directory name
# @pytest.mark.usefixtures("enterprise_only")
# def test_create_project_with_conflicting_id_path(rest, tmp_project):
#     project_dir = rest.get_upload_dir(tmp_project.id)
#     upload_root = os.path.dirname(project_dir)
#
#     # make a file <next project id> in the upload dir
#     next_project_id = tmp_project.id + 1
#     next_dir = os.path.join(upload_root, str(next_project_id))
#
#     open(next_dir, "w").write("some text")
#
#     # try to make a project. It should still succeed (how?)
#     next_proj = ProjectClient.make(rest, name="next proj")
#     with pytest.raises(Exception, match="500"):
#         # TODO: uploading shouldn't be necessary
#         # upload something so the directory is created
#         rest.post_file("/upload", __file__, "testfile", next_proj.id)
