from contextlib import contextmanager
import os
import pytest
from assertions import (
    assert_is_subdict,
    has_expected_files,
    assert_eventually,
    task_is_complete,
)

SAMPLE_ZIP = os.path.join(os.path.dirname(__file__), "Archive.zip")
SAMPLE_ZIP_FILES = ["1.txt", "2.txt"]

def split_and_keep(string, separator):
    without_sep = string.split(separator)
    return [s + separator for s in without_sep[:-1]] + without_sep[-1:]


def lines_from_utf8(filename):
    as_bytes = open(filename, "rb").read()
    without_bom = as_bytes[3:]
    as_str = without_bom.decode()
    return split_and_keep(as_str, "\n")


def clean_files_from_server(rest, files, project_id):
    upload_dir = rest.get_upload_dir(project_id)
    paths = (os.path.join(upload_dir, f) for f in files)
    for p in paths:
        try:
            rest.delete("/files", path=p, project_id=project_id)
        except:
            # don't care if the file isn't there
            pass


@contextmanager
def clean_uploads_dir(rest, files, project_id):
    clean_files_from_server(rest, files, project_id)
    try:
        yield
    finally:
        clean_files_from_server(rest, files, project_id)


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
def test_upload_utf8_file_roundtrip(rest, tmp_utf8_file, tmp_project):
    remote_path = os.path.join(rest.get_upload_dir(tmp_project.id), "utf8file")

    with clean_uploads_dir(rest, ["utf8file"], tmp_project.id):
        # Step 1: upload
        ret = rest.post_file("/upload", tmp_utf8_file, "utf8file", tmp_project.id, overwrite=True)
        assert ret

        # Step 2: download
        ret = rest.get("/files/get_file_content", path=remote_path, project_id=tmp_project.id)
        assert ret

        expected = {"file_contents": lines_from_utf8(tmp_utf8_file)}
        assert ret == expected


@pytest.mark.timeout(1)
@pytest.mark.usefixtures('enterprise_only')
def test_upload_file(rest, tmp_text_file, tmp_project):
    with clean_uploads_dir(rest, ["uploadedfile"], tmp_project.id):
        ret = rest.post_file("/upload", tmp_text_file, "uploadedfile", tmp_project.id, overwrite=True)

        expected = {
            "name": "uploadedfile",
            "size": os.path.getsize(tmp_text_file),
        }
        assert_is_subdict(ret, expected)

        # test that we can round-trip the data back out of the API
        ret = rest.get("/upload", filename="uploadedfile", project_id=tmp_project.id)
        assert_is_subdict(ret, expected)


@pytest.mark.timeout(30)
@pytest.mark.usefixtures('enterprise_only')
def test_upload_zip(rest, tmp_project):
    UNZIPPED_PATHS = [os.path.join("destfilename", f) for f in SAMPLE_ZIP_FILES]
    EXPECTED_FILES = ["destfilename.zip", *UNZIPPED_PATHS]
    with clean_uploads_dir(rest, EXPECTED_FILES, tmp_project.id):
        ret = rest.post_file("/upload", SAMPLE_ZIP, "destfilename.zip", tmp_project.id, overwrite=True)

        # wait for the zip to show up
        assert_eventually(has_expected_files, rest, tmp_project.id, ["destfilename.zip"], None, stop_max_delay=5000, wait_fixed=100)

        # wait for unzip to complete
        assert_eventually(task_is_complete, rest, ret["task_id"], stop_max_delay=5000, wait_fixed=100)

        assert has_expected_files(rest, tmp_project.id, SAMPLE_ZIP_FILES, "destfilename")
