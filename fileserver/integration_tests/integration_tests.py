import sys
import rest

usingDocker = True

if usingDocker:
    host = "localhost"
    home = "/perceptilabs"
    platform = "Linux"
    tutorial_data = "/opt/app-root/src/perceptilabs/tutorial_data"
else:
    host = "localhost"
    home = "/Users/j"
    platform = "Darwin"
    tutorial_data = '/Users/j/f/modeling/perceptilabs/tutorial_data'

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
