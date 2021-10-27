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


def clean_files_from_server(rest, files):
    paths = (os.path.join(rest.upload_dir, f) for f in files)
    for p in paths:
        rest.delete("/files", path=p)


@contextmanager
def clean_uploads_dir(rest, files):
    clean_files_from_server(rest, files)
    try:
        yield
    finally:
        clean_files_from_server(rest, files)


@pytest.mark.timeout(1)
def test_upload_utf8_file_roundtrip(rest, tmp_utf8_file):
    if not rest.is_enterprise:
        return

    remote_path = os.path.join(rest.upload_dir, "utf8file")

    with clean_uploads_dir(rest, ["utf8file"]):
        # Step 1: upload
        ret = rest.post_file("/upload", tmp_utf8_file, "utf8file", overwrite=True)
        assert ret

        # Step 2: download
        ret = rest.get("/files/get_file_content", path=remote_path)
        assert ret

        expected = {"file_contents": lines_from_utf8(tmp_utf8_file)}
        assert ret == expected


@pytest.mark.timeout(1)
def test_upload_file(rest, tmp_text_file):
    if not rest.is_enterprise:
        return

    with clean_uploads_dir(rest, ["uploadedfile"]):
        ret = rest.post_file("/upload", tmp_text_file, "uploadedfile", overwrite=True)

        expected = {
            "name": "uploadedfile",
            "size": os.path.getsize(tmp_text_file),
        }
        assert_is_subdict(ret, expected)

        # test that we can round-trip the data back out of the API
        ret = rest.get("/upload", filename="uploadedfile")
        assert_is_subdict(ret, expected)


@pytest.mark.timeout(30)
def test_upload_zip(rest):
    if not rest.is_enterprise:
        return

    UNZIPPED_PATHS = [os.path.join("destfilename", f) for f in SAMPLE_ZIP_FILES]
    EXPECTED_FILES = ["destfilename.zip", *UNZIPPED_PATHS]
    with clean_uploads_dir(rest, EXPECTED_FILES):
        ret = rest.post_file("/upload", SAMPLE_ZIP, "destfilename.zip", overwrite=True)

        # wait for the zip to show up
        assert_eventually(has_expected_files, rest, ["destfilename.zip"], None, stop_max_delay=5000, wait_fixed=100)

        # wait for unzip to complete
        assert_eventually(task_is_complete, rest, ret["task_id"], stop_max_delay=5000, wait_fixed=100)

        assert has_expected_files(rest, SAMPLE_ZIP_FILES, "destfilename")
