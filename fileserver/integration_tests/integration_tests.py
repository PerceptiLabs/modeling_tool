#!/usr/bin/env python
import os
import sys
import rest
import tempfile
import json
import platform
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

usingDocker = False
if len(sys.argv) < 2:
    print(f"USAGE: {sys.argv[0]} <docker-tag>|local")
    print(f"Example: {sys.argv[0]} 1234")
    print(f"Example: {sys.argv[0]} local")
    sys.exit(1)

if sys.argv[1] == 'local':
    # uses "containe=1" to trick the server into thinking it's in a container
    CMD = "PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data container=1 python manage.py runserver 8011"
    host = "localhost"
    home = os.getenv("HOME")
    platform = platform.system()
    TUTORIAL_DATA_RELPATH="../../backend/perceptilabs/tutorial_data"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tutorial_data = os.path.abspath(os.path.join(script_dir, TUTORIAL_DATA_RELPATH))
else:
    CMD='docker run -it --env "HOME=/perceptilabs" --env "PL_TUTORIALS_DATA=/tutorial_data" --publish 8011:8011 --volume $(pwd)/plabs:/perceptilabs/Documents/Perceptilabs percepilabs.azurecr.io/kernel:' + sys.argv[1]
    host = "localhost"
    home = "/perceptilabs"
    platform = "Linux"
    tutorial_data = "/tutorial_data"

rest = rest.FileserverRest(f"http://{host}:8011", "thetoken")

while True:
    try:
        rest.check()
        break
    except:
        print("start the fileserver with the following:")
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

print("ok")
