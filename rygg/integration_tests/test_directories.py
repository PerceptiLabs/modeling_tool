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

	# Gets drives on Windows. Doesn't try otherwise
	if platform.system() == "Windows":
		assert rest.get("/directories/drives")
	else:
		assert rest.get("/directories/drives") == None


@pytest.mark.usefixtures('localhost_only')
@pytest.mark.usefixtures('enterprise_only')
def test_localhost_specific_items_enterprise(host, rest, tmp_project):

	# Can't access file by full path outside the project
	with pytest.raises(Exception, match="404"):
		rest.get("/files", path=MY_PATH, project_id=tmp_project.id)

	# Fails to find nonexistent file
	with pytest.raises(Exception):
		rest.get("/files", path=MY_PATH+"_nonexistent", project_id=tmp_project.id)

	# Doesn't support home dir
	with pytest.raises(Exception, match="400"):
		rest.get("/directories/resolved_dir", path="~", project_id=tmp_project.id)

	# Doesn't support drives
	assert rest.get("/directories/drives") == None


@pytest.mark.usefixtures('enterprise_only')
def test_resolved_dir_works_enterprise(rest, tmp_project):
    working_dir = rest.get_upload_dir(tmp_project.id)

    def go(path):
        return rest.get("/directories/resolved_dir", path=path, project_id=tmp_project.id)

    # enterprise should refuse to expand ~
    with pytest.raises(Exception):
        go("~/a")

    expected = os.path.join(working_dir, "a")
    assert go("a") == {"path": expected}


@pytest.mark.usefixtures('pip_only')
def test_resolved_dir_works_pip(rest, tmp_project):
    def go(path):
        return rest.get("/directories/resolved_dir", path=path, project_id=tmp_project.id)

    expected = {"path": os.path.expanduser('~/a')}
    assert go("~/a") == expected
    # on pip, we don't expand the dir to a project directory
    assert go("a") == expected


@pytest.mark.usefixtures('pip_only')
def test_post_delete_directories_pip(rest, tmp_project):

    working_dir = rest.get("/directories/resolved_dir", path="~/Documents/Perceptilabs", project_id=tmp_project.id)["path"]

    def is_dir_present(rest, home_dir, project_id):
        check_resp = rest.get("/directories/get_folder_content", path=f"{home_dir}/Documents/Perceptilabs", project_id=project_id)
        return "plabs" in check_resp["dirs"]

    # make a directory
    rest.post("/directories", {}, path= f"{working_dir}/plabs", project_id=tmp_project.id)

    # make sure it's there
    project_id = tmp_project.id
    home_dir = rest.get("/directories/resolved_dir", path="~", project_id=project_id)["path"]
    assert is_dir_present(rest, home_dir, project_id)

    # do the deletion
    rest.delete("/directories", path=f"{working_dir}/plabs", project_id=tmp_project.id)

    # check that it's gone
    assert not is_dir_present(rest, home_dir, project_id)


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
