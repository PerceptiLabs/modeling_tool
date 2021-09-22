import os
import pytest
import time

from rest import RyggRest
from clients import ProjectClient, ModelClient, NotebookClient, DatasetClient

def test_project_delete(rest):
    with ProjectClient.make(rest, name="test project") as project:
        pass

    with pytest.raises(Exception, match="404"):
        project.fetch()

def test_project_delete_also_deletes_model(rest):
    with ProjectClient.make(rest, name="test project") as project:
        model = ModelClient.make(rest, project=project.id, name="model name")

    with pytest.raises(Exception, match="404"):
        model.fetch()

def test_project_delete_also_deletes_dataset(rest, tmp_text_file):
    if rest.is_enterprise():
        filename = os.path.basename(tmp_text_file)
    else:
        filename = tmp_text_file

    with ProjectClient.make(rest, name="test project") as project:
        dataset = DatasetClient.make(rest, name="some file", location=filename, project=project.id, models=[])

    with pytest.raises(Exception, match="404"):
        dataset.fetch()

def test_project_delete_also_deletes_notebook(rest):
    with ProjectClient.make(rest, name="test project") as project:
        notebook = NotebookClient.make(rest, project=project.id, name="notebook1")

    with pytest.raises(Exception, match="404"):
        notebook.fetch()

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

