import os
import sys
import rest

usingDocker = False
if len(sys.argv) < 2:
    print(f"USAGE: {sys.argv[0]} <docker-tag>|local")
    print(f"Example: {sys.argv[0]} 1234")
    print(f"Example: {sys.argv[0]} local")
    sys.exit(1)

if sys.argv[1] == 'local':
    CMD = "PL_FILE_SERVING_TOKEN=thetoken PL_TUTORIALS_DATA=$(git rev-parse --show-toplevel)/backend/perceptilabs/tutorial_data python manage.py runserver 8011"
    host = "localhost"
    home = os.getenv("HOME")
    platform = "Darwin"
    TUTORIAL_DATA_RELPATH="../../backend/perceptilabs/tutorial_data"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tutorial_data = os.path.abspath(os.path.join(script_dir, TUTORIAL_DATA_RELPATH))
else:
    CMD='docker run -it --env "HOME=/perceptilabs" --env "PL_TUTORIALS_DATA=/tutorial_data" --publish 8011:8011 --volume $(pwd)/plabs:/perceptilabs/Documents/Perceptilabs percepilabs.azurecr.io/kernel:' + sys.argv[1]
    host = "localhost"
    home = "/perceptilabs"
    platform = "Linux"
    tutorial_data = "/tutorial_data"

print("start the fileserver with the following:")
print(CMD)
input("Press enter to continue")

rest = rest.FileserverRest(f"http://{host}:8011", "thetoken")

# check connectivity
rest.check()
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

print("ok")
