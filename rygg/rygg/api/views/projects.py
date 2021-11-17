from django_http_exceptions import HTTPExceptions
from rest_framework import viewsets

from rygg.api.models import Project
from rygg.api.serializers import ProjectSerializer
from rygg.api.views.models import ModelViewSet
from rygg.settings import IS_CONTAINERIZED
from rygg.files.views.util import protect_read_only_enterprise_field

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.available_objects.filter(is_removed=False).order_by("-project_id")
    serializer_class = ProjectSerializer

    def create(self, request):
        protect_read_only_enterprise_field(request, 'default_directory')
        return super().create(request)

    def update(self, request, **kwargs):
        protect_read_only_enterprise_field(request, 'default_directory')
        return super().update(request, **kwargs)
