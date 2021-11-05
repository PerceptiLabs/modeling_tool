import os

def test_post_json_models(rest, tmp_project):
    if rest.is_enterprise:
        working_dir = rest.get_upload_dir(tmp_project.id)
    else:
        working_dir = os.getcwd()

    rest.post("/json_models", {"this": "is a jsonfile"},  path= f"simple_model", project_id=tmp_project.id)
    assert "model.json" in rest.get("/directories/get_folder_content", path=f"simple_model", project_id=tmp_project.id)["files"]

