import os
import platform
import pytest

MY_PATH = os.path.realpath(__file__)
RYGG_SERVER_DIR = os.path.normpath(os.path.join(MY_PATH, "..", ".."))


@pytest.mark.usefixtures('localhost_only')
@pytest.mark.usefixtures('pip_only')
def test_localhost_specific_items_pip(host, rest, tmp_project):

    # Can access file by full path outside the project
    resp = rest.get("/files", path=MY_PATH, project_id=tmp_project.id)
    assert resp["path"] == MY_PATH

    # Fails to find nonexistent file
    with pytest.raises(Exception):
        rest.get("/files", path=MY_PATH+"_nonexistent", project_id=tmp_project.id)

    # Properly resolves ~
    home = os.getenv("HOME")
    assert rest.get("/directories/resolved_dir", path="~", project_id=tmp_project.id) == {"path": home}


@pytest.mark.usefixtures('localhost_only')
@pytest.mark.usefixtures('enterprise_only')
def test_localhost_specific_items_enterprise(host, rest, tmp_project):

    with pytest.raises(Exception, match="400"):
        rest.get("/files", path=MY_PATH, project_id=tmp_project.id)

    # Doesn't support home dir
    with pytest.raises(Exception, match="400"):
        rest.get("/directories/resolved_dir", path="~", project_id=tmp_project.id)


@pytest.mark.usefixtures('enterprise_only')
def test_resolved_dir_rejected_enterprise(rest, tmp_project):
    working_dir = rest.get_upload_dir(tmp_project.id)

    def go(path):
        return rest.get("/directories/resolved_dir", path=path, project_id=tmp_project.id)

    # enterprise should refuse to expand ~
    with pytest.raises(Exception):
        go("~/a")

    with pytest.raises(Exception):
        go("a")


@pytest.mark.usefixtures('pip_only')
def test_resolved_dir_works_pip(rest, tmp_project):
    def go(path):
        return rest.get("/directories/resolved_dir", path=path, project_id=tmp_project.id)

    expected = {"path": os.path.expanduser('~/a')}
    assert go("~/a") == expected
    # on pip, we don't expand the dir to a project directory
    assert go("a") == expected


@pytest.mark.usefixtures('enterprise_only')
def test_post_directories_enterprise(rest, tmp_project):
    # post anything. It should return 422 since enterprise doesn't allow you to post a directory
    my_dir = os.path.dirname(__file__)
    with pytest.raises(Exception, match="422"):
        rest.post("/directories", {}, path=my_dir, project_id=tmp_project.id)["path"]


@pytest.mark.usefixtures('enterprise_only')
def test_directory_chooser_enterprise(rest):
    with pytest.raises(Exception, match="404"):
        rest.get("/directories/pick_directory", initial_dir="~")


@pytest.mark.usefixtures('pip_only')
def test_directory_chooser(rest):
    rest.get("/directories/pick_directory", initial_dir=os.getcwd(), title="testing title")
