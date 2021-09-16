import os
from assertions import (
                        assert_is_subdict,
                        has_expected_files,
                        assert_eventually,
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


def test_upload_utf8_file_roundtrip(rest, tmp_utf8_file):
    upload_dir = rest.get("/upload_dir")["path"]
    remote_path = os.path.join(upload_dir, "destfilename")

    # Step 0: Make sure that the file isn't there
    rest.delete("/files", path=remote_path)
    ret = rest.get("/files/get_file_content", path=remote_path)
    assert not ret

    # Step 1: upload
    ret = rest.post_file("/upload", tmp_utf8_file, "destfilename", overwrite=True)
    assert ret

    # Step 2: download
    ret = rest.get("/files/get_file_content", path=remote_path)
    assert ret

    expected = {"file_contents": lines_from_utf8(tmp_utf8_file)}
    assert ret == expected


def test_upload_file(rest, tmp_text_file):
    ret = rest.post_file("/upload", tmp_text_file, "destfilename", overwrite=True)

    expected = {
        "name": "destfilename",
        "size": os.path.getsize(tmp_text_file),
    }
    assert_is_subdict(ret, expected)

    # test that we can round-trip the data back out of the API
    ret = rest.get("/upload", filename="destfilename")
    assert_is_subdict(ret, expected)


def clean_files_from_server(rest, files):
    for f in files:
        rest.delete("/files", path=f)

def test_upload_zip(rest):
    EXPECTED_FILES = ["destfilename.zip", *SAMPLE_ZIP_FILES]

    clean_files_from_server(rest, EXPECTED_FILES)

    ret = rest.post_file("/upload", SAMPLE_ZIP, "destfilename.zip", overwrite=True)

    # Make sure that the upload started a task
    assert ret["task_id"]
    task = rest.get(f"/tasks/{ret['task_id']}/")
    assert task["state"] in ["PENDING", "COMPLETED"]

    # Wait for the files to show up
    assert_eventually(has_expected_files, EXPECTED_FILES, stop_max_delay=60000, wait_fixed=1000)
