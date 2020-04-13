import dateutil.parser
import time
import rest


def make_project(name):
    resp = rest.post("/projects/", name=name)
    project_id = resp["project_id"]
    print(f"made project #{project_id}")
    return project_id


def get_project(project_id):
    return rest.get(f"/projects/{project_id}/")


def rename_project(project_id, **kwargs):
    rest.patch(f"/projects/{project_id}/", **kwargs)
    return get_project(project_id)


def test_update(proj):
    time.sleep(0.1)  # just enough to put a gap between create and update date
    proj = rename_project(project_id, name="this is a new name")

    created_str = proj["created"]
    created = dateutil.parser.parse(created_str)

    updated_str = proj["updated"]
    updated = dateutil.parser.parse(updated_str)

    diff = updated - created
    if updated == created:
        raise Exception("Expected updated to be after created")

def delete_project(project_id):
    rest.delete(f"/projects/{project_id}/")

def make_model(project, name):
    resp = rest.post("/models/",
            name=name,
            project=project)
    model_id = resp["model_id"]
    print(f"made model #{model_id} in project #{project}")
    return model_id

def delete_model(model_id):
    rest.delete(f"/models/{model_id}/")

rest.check()
project_id = make_project("test project")
proj = get_project(project_id)
test_update(proj)
model_id = make_model(project_id, "lala")
delete_model(model_id)
delete_project(project_id)

print("Success!!")
