import os
import pytest
import time

from rest import RyggRest
from clients import ProjectClient, ModelClient, NotebookClient, DatasetClient
from assertions import assert_eventually


@pytest.mark.usefixtures('enterprise_only')
def test_save_json_round_trips(tmp_model):
    data = {"this": "is a jsonfile"}

    tmp_model.save_json(data)
    resp = tmp_model.get_json()
    assert resp == {"model_body": data}

@pytest.mark.timeout(0.2)
def test_model_requires_project(rest, tmp_project):
    with pytest.raises(Exception, match="400"):
        ModelClient.make(rest, name="m")

    with ModelClient.make(rest, name="m", project=tmp_project.id):
        pass


@pytest.mark.timeout(0.2)
@pytest.mark.usefixtures('enterprise_only')
def test_new_model_has_extant_location(rest, tmp_project):
    with ModelClient.make(rest, name="test project", project=tmp_project.id) as model:
        model.refresh()
        assert os.path.isdir(model.location)

    assert_eventually(lambda: not os.path.exists(model.location), stop_max_delay=1000, wait_fixed=100)


@pytest.mark.timeout(0.2)
@pytest.mark.usefixtures('enterprise_only')
def test_new_model_rejects_location(rest, tmpdir, tmp_project):
    with pytest.raises(Exception):
        with ModelClient.make(rest, name="test project", project=tmp_project.id, location=str(tmpdir)) as model:
            pass

@pytest.mark.timeout(0.2)
@pytest.mark.usefixtures('enterprise_only')
def test_cant_update_model_location(rest, tmpdir, tmp_project):
    with ModelClient.make(rest, name="test project", project=tmp_project.id) as model:
        with pytest.raises(Exception, match="400.*location"):
            model.update(location = str(tmpdir))


@pytest.mark.timeout(0.4)
@pytest.mark.usefixtures('enterprise_only')
def test_next_name_works(rest, tmp_project):
    # gets " 1" when there are no others with a number
    assert ModelClient.get_next_name(rest, tmp_project.id, "this_is_a_prefix")['next_name'] == "this_is_a_prefix 1"

    ModelClient.make(rest, project=tmp_project.id, name="this_is_a_prefix")
    assert ModelClient.get_next_name(rest, tmp_project.id, "this_is_a_prefix")['next_name'] == "this_is_a_prefix 1"

    # gets "2" if there's one with the prefix but no number
    ModelClient.make(rest, project=tmp_project.id, name="this_is_a_prefix 11")
    assert ModelClient.get_next_name(rest, tmp_project.id, "this_is_a_prefix")['next_name'] == "this_is_a_prefix 12"

@pytest.mark.timeout(0.2)
@pytest.mark.usefixtures('pip_only')
def test_user_home_used(rest, tmp_project):
    from pathlib import Path
    dest = os.path.join("~", "pltest")
    try:
        with ModelClient.make(rest, name="test project", project=tmp_project.id, location=dest) as model:
            model.save_json({})

            expected = os.path.join(Path.home(), "pltest", "model.json")
            assert os.path.isfile(expected)
    finally:
        import shutil
        shutil.rmtree(dest, ignore_errors=True)
