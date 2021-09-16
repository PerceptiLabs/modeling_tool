
def test_post_json_models(working_dir, rest):
    rest.post("/json_models", {"this": "is a jsonfile"},  path= f"{working_dir}/simple_model")
    assert "model.json" in rest.get("/directories/get_folder_content", path=f"{working_dir}/simple_model")["files"]

