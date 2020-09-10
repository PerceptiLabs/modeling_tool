from django.urls import path
from fileserver.api.views.file_view import FileView
from fileserver.api.views.directory_view import DirectoryView, get_tutorial_data
from fileserver.api.views.json_model_view import JsonModelView
from fileserver.api.views.model_directory_view import (modeldirectory_tree, get_modeldirectory)
from fileserver.api.views.github_view import (github_export, github_import)

urlpatterns = [
    path("files", FileView.as_view()),
    path("json_models", JsonModelView.as_view()),
    path("directories", DirectoryView.as_view()),
    path("directories/tutorial_data", get_tutorial_data),
    path("modeldirectories/tree", modeldirectory_tree),
    path("modeldirectories", get_modeldirectory),
    path(r"github/export", github_export),
    path(r"github/import", github_import),
]
