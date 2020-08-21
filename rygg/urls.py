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
from rygg.api import views

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)
router.register(r"models", views.ModelViewSet)
router.register(r"notebooks", views.NotebookViewSet)
router.register(r"issues", views.IssuesViewSet, basename='Issues')

urlpatterns = [
    path("", (include(router.urls))),
    path(r"app/version/", views.get_version),
    path(r"app/updates_available/", views.get_updates_available),
]
