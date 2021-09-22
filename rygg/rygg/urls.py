from django.urls import include, path
from rest_framework import routers
from rygg.api.views import (
    get_version,
    get_updates_available,
    is_enterprise,
)
from rygg.api.views.projects import ProjectViewSet
from rygg.api.views.models import ModelViewSet
from rygg.api.views.datasets import DatasetViewSet
from rygg.api.views.notebooks import NotebookViewSet
from rygg.api.views.issues import IssuesViewSet
from rygg.api.views.tasks import TaskViewSet
from rygg.mixpanel_proxy import views as mixpanel_views

from rygg.files.views.file_view import (
        FileView,
        get_file_content
)
from rygg.files.views.directory_view import (
        DirectoryView,
        get_tutorial_data,
        get_drives,
        get_folder_content,
        get_resolved_dir,
        get_root_path,
        )
from rygg.files.views.json_model_view import JsonModelView
from rygg.files.views.model_directory_view import (modeldirectory_tree, get_modeldirectory)
from rygg.files.views.github_view import (github_export, github_import, github_issue)
from rygg.files.views.url_reachable import is_url_reachable
from rygg.files.views.upload_view import UploadView, get_upload_dir


router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"models", ModelViewSet)
router.register(r"datasets", DatasetViewSet)
router.register(r"notebooks", NotebookViewSet)
router.register(r"issues", IssuesViewSet, basename='Issues')
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", (include(router.urls))),
    path(r"app/version/", get_version),
    path(r"app/updates_available/", get_updates_available),
    path(r"app/is_enterprise/", is_enterprise),
    path('mixpanel/track/', mixpanel_views.track),
    path('mixpanel/decide/', mixpanel_views.decide),
    path('mixpanel/engage/', mixpanel_views.engage),
    path("files", FileView.as_view()),
    path("files/get_file_content", get_file_content),
    path("json_models", JsonModelView.as_view()),
    path("directories", DirectoryView.as_view()),
    path("directories/tutorial_data", get_tutorial_data),
    path("directories/drives", get_drives),
    path("directories/get_folder_content", get_folder_content),
    path("directories/resolved_dir", get_resolved_dir),
    path("directories/root", get_root_path),
    path("modeldirectories/tree", modeldirectory_tree),
    path("modeldirectories", get_modeldirectory),
    path(r"github/export", github_export),
    path(r"github/import", github_import),
    path(r"github/issue", github_issue),
    path("is_url_reachable", is_url_reachable),
    path(r"upload", UploadView.as_view()),
    path(r"upload_dir", get_upload_dir),
]
