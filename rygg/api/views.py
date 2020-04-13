from rest_framework import viewsets
from rest_framework import permissions
from rygg.api.models import Project, Model
from rygg.api.serializers import ProjectSerializer, ModelSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-project_id")
    serializer_class = ProjectSerializer


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
