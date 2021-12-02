import os
import pytest
import time
from pathlib import Path

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


@pytest.mark.usefixtures('pip_only')
def test_project_delete_also_deletes_dataset(rest, tmp_text_file):
    with ProjectClient.make(rest, name="test project") as project:
        dataset = DatasetClient.make(rest, name="some file", location=tmp_text_file, project=project.id, models=[])

    assert not dataset.exists


@pytest.mark.usefixtures('pip_only')
def test_project_delete_also_deletes_dataset(rest, tmp_text_file):
    with ProjectClient.make(rest, name="test project") as project:
        dataset = DatasetClient.make(rest, name="some file", project=project.id, models=[], location=str(tmp_text_file))

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

@pytest.mark.usefixtures('pip_only')
def test_allows_default_directory_in_local(rest, tmpdir):
    with ProjectClient.make(rest, name="name", default_directory=str(tmpdir)):
        pass

@pytest.mark.usefixtures('enterprise_only')
def test_create_rejects_default_directory_in_enterprise(rest, tmpdir):
    with pytest.raises(Exception, match="400.*default_directory"):
        ProjectClient.make(rest, name="name", default_directory=str(tmpdir))

@pytest.mark.usefixtures('enterprise_only')
def test_update_rejects_default_directory_in_enterprise(rest, tmpdir, tmp_project):
    with pytest.raises(Exception, match="400.*default_directory"):
        tmp_project.update(default_directory=str(tmpdir))


DEFAULT_PATH = os.path.join(Path.home(), "Documents", "Perceptilabs", "Default")
@pytest.mark.skipif(not Path.home(), reason="Default project requires a HOME directory")
@pytest.mark.skipif(os.path.isdir(DEFAULT_PATH), reason="Default project requires a HOME directory")
def test_get_default_mode_project(rest):
    assert not os.path.isdir(DEFAULT_PATH)
    p = ProjectClient.get_default(rest)
    assert os.path.isdir(p.default_directory)
    assert p.default_directory == DEFAULT_PATH

