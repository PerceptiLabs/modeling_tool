from rest_framework import viewsets
from rygg.api.models import Project
from rygg.api.serializers import ProjectSerializer
from rygg.api.views.models import ModelViewSet

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.available_objects.filter(is_removed=False).order_by("-project_id")
    serializer_class = ProjectSerializer
