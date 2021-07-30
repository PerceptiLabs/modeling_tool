"""rygg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin

from django.urls import include, path
from rest_framework import routers
from rygg.api import views as api_views
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
from rygg.files.views.upload_view import UploadView


router = routers.DefaultRouter()
router.register(r"projects", api_views.ProjectViewSet)
router.register(r"models", api_views.ModelViewSet)
router.register(r"notebooks", api_views.NotebookViewSet)
router.register(r"issues", api_views.IssuesViewSet, basename='Issues')

urlpatterns = [
    path("", (include(router.urls))),
    path(r"app/version/", api_views.get_version),
    path(r"app/updates_available/", api_views.get_updates_available),
    path(r"app/is_enterprise/", api_views.is_enterprise),
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
]
