#!/usr/bin/env python
import os
import sys
import rest
from retrying import retry
import tempfile
import json, time
import platform
import zipfile
from contextlib import contextmanager

@contextmanager
def populated_tempfile(content_str):
    content_bytes=bytearray(content_str.encode('utf-8'))
    with populated_bin_tempfile(content_bytes) as f:
        yield f

@contextmanager
def populated_bin_tempfile(content_bytes):
    with tempfile.TemporaryDirectory() as td:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=td) as f:
            f.write(content_bytes)
            f.close()
            yield f.name

if len(sys.argv) < 2:
    print(f"USAGE: {sys.argv[0]} <docker-tag>|local")
    print(f"Example: {sys.argv[0]} 1234")
    print(f"Example: {sys.argv[0]} local")
    sys.exit(1)

if sys.argv[1] == 'local':
    # uses "containe=1" to trick the server into thinking it's in a container
    CMD = "PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data container=1 python manage.py runserver 8000"
    host = "localhost"
    home = os.getenv("HOME")
    platform = platform.system()
    TUTORIAL_DATA_RELPATH="../../backend/perceptilabs/tutorial_data"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tutorial_data = os.path.abspath(os.path.join(script_dir, TUTORIAL_DATA_RELPATH))
else:
    CMD='docker run -it --env "HOME=/perceptilabs" --env "PL_TUTORIALS_DATA=/tutorial_data" --publish 8000:8000 --volume $(pwd)/plabs:/perceptilabs/Documents/Perceptilabs percepilabs.azurecr.io/kernel:' + sys.argv[1]
    host = "localhost"
    home = "/perceptilabs"
    platform = "Linux"
    tutorial_data = "/tutorial_data"

rest = rest.RyggRest(f"http://{host}:8000", "thetoken")

while True:
    try:
        rest.check()
        break
    except:
        print("start rygg with the following:")
        print(CMD)
        input("Press enter to continue")

# check connectivity
assert rest.head("/files", path="manage.py")
assert rest.get("/directories/resolved_dir", path="a") == {"path": "a"}

# the home directory has to resolve to /perceptilabs for docker
assert rest.get("/directories/resolved_dir", path="~") == {"path": home}

assert rest.get("/directories/drives") == None

# get_folder_content doesn't expand user folders
assert rest.get("/directories/get_folder_content", path="~") == {'current_path': '', 'dirs': '', 'files': '', 'platform': platform}
working_dir = rest.get("/directories/resolved_dir", path="~/Documents/Perceptilabs")["path"]
rest.post("/directories", {}, path= f"{working_dir}/plabs")

assert "plabs" in rest.get("/directories/get_folder_content", path=f"{home}/Documents/Perceptilabs")["dirs"]
rest.delete("/directories", path=f"{working_dir}/plabs")
assert "plabs" not in rest.get("/directories/get_folder_content", path=f"{home}/Documents/Perceptilabs")["dirs"]

rest.post("/json_models", {"this": "is a jsonfile"},  path= f"{working_dir}/simple_model")

assert "model.json" in rest.get("/directories/get_folder_content", path=f"{working_dir}/simple_model")["files"]

assert rest.get("/directories/tutorial_data") == {'path': tutorial_data}

# upload a UTF-8 file with a BOM
content_str="""
this is some
text
"""
bin_file=bytearray([0xef, 0xbb, 0xbf])
bin_file.extend(content_str.encode("ascii"))

with populated_bin_tempfile(bin_file) as filename:
    ret=rest.post_file("/upload", filename, "destfilename", overwrite=True)

    expected = {
        "name": "destfilename",
        "size": len(bin_file),
        # yep, we're expecting what we got
        # it'll fail if those fields are missing, and that's all we care about
        "created": ret["created"],
        "modified": ret["modified"],
    }
    assert ret == expected

    # test that we can round-trip the data back out of the API
    ret = rest.get("/upload", filename="destfilename")
    assert ret == expected

    # Response should match (except for some newlines)
    expected = {'file_contents': [l+"\n" for l in content_str.split('\n')][:-1]}
    assert rest.get("/files/get_file_content", path=filename) == expected

SAMPLE_ZIP = os.path.join(os.path.dirname(__file__), "Archive.zip")
EXPECTED_FILES = ["destfilename.zip", "1.txt", "2.txt"]

# we need the UPLOAD_PATH if we're using docker
UPLOAD_PATH=os.getenv("PL_FILE_UPLOAD_DIR")
usingDocker = rest.get("/app/is_enterprise")["is_enterprise"]
if usingDocker:
    assert UPLOAD_PATH and os.path.isdir(UPLOAD_PATH)

# make sure the directory is clean
for f in [os.path.join(UPLOAD_PATH, fn) for fn in EXPECTED_FILES]:
    try:
        os.remove(f)
    except FileNotFoundError:
        pass

ret = rest.post_file("/upload", SAMPLE_ZIP, "destfilename.zip", overwrite=True)

assert ret["task_id"]

@retry(stop_max_delay=60000, wait_fixed=1000)
def get_unzipped_files():
    got = rest.get("/directories/get_folder_content", path=UPLOAD_PATH)
    assert set(EXPECTED_FILES) <= set(got["files"])

get_unzipped_files()

print("ok")
