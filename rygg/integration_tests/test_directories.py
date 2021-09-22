import os
import platform
import pytest

def test_localhost_specific_items(host, rest):
    if host not in ["localhost", "127.0.0.1"]:
        pytest.skip()

    home = os.getenv("HOME")
    assert rest.head("/files", path="manage.py")
    assert rest.get("/directories/resolved_dir", path="~") == {"path": home}

    if platform.system() == "Windows":
        assert rest.get("/directories/drives")
    else:
        assert rest.get("/directories/drives") == None

    # get_folder_content doesn't expand user folders
    # Assumes the same platform
    assert rest.get("/directories/get_folder_content", path="~") == {'current_path': '', 'dirs': '', 'files': '', 'platform': platform.system()}


def test_resolved_dir_works(rest):
    assert rest.get("/directories/resolved_dir", path="a") == {"path": "a"}


def test_post_delete_directories(rest, working_dir):
    rest.post("/directories", {}, path= f"{working_dir}/plabs")
    home_dir = rest.get("/directories/resolved_dir", path="~")["path"]
    assert "plabs" in rest.get("/directories/get_folder_content", path=f"{home_dir}/Documents/Perceptilabs")["dirs"]
    rest.delete("/directories", path=f"{working_dir}/plabs")
    assert "plabs" not in rest.get("/directories/get_folder_content", path=f"{home_dir}/Documents/Perceptilabs")["dirs"]


