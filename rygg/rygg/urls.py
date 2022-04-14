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
    pick_file,
    saveas_file,
)
from rygg.files.views.directory_view import (
    DirectoryView,
    get_resolved_dir,
    pick_directory,
)
from rygg.files.views.github_view import github_export, github_import, github_issue
from rygg.files.views.upload_view import get_upload_dir
from rygg.files.views.tf_hub_cache_view import get_tf_hub_cache_dir

router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"models", ModelViewSet, basename="Models")
router.register(r"datasets", DatasetViewSet, basename="Datasets")
router.register(r"notebooks", NotebookViewSet)
router.register(r"issues", IssuesViewSet, basename="Issues")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", (include(router.urls))),
    path(r"app/version/", get_version),
    path(r"app/updates_available/", get_updates_available),
    path(r"app/is_enterprise/", is_enterprise),
    path("mixpanel/track/", mixpanel_views.track),
    path("mixpanel/decide/", mixpanel_views.decide),
    path("mixpanel/engage/", mixpanel_views.engage),
    path("files", FileView.as_view()),
    path("files/pick_file", pick_file),
    path("files/saveas_file", saveas_file),
    path("directories", DirectoryView.as_view()),
    path("directories/pick_directory", pick_directory),
    path("directories/resolved_dir", get_resolved_dir),
    path(r"github/export", github_export),
    path(r"github/import", github_import),
    path(r"github/issue", github_issue),
    path(r"upload_dir", get_upload_dir),
    path(r"tf_hub_cache_dir", get_tf_hub_cache_dir),
]
