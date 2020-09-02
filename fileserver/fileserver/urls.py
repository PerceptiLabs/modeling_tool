from django.urls import path
from fileserver.api.views import FileView, DirectoryView, JsonModelView

urlpatterns = [
    path("files", FileView.as_view()),
    path("json_models", JsonModelView.as_view()),
    path("directories", DirectoryView.as_view()),
]
