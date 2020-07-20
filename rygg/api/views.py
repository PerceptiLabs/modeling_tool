from rest_framework import viewsets
from rest_framework import permissions
from rygg.api.models import Project, Model, Notebook
from rygg.api.serializers import ProjectSerializer, ModelSerializer, NotebookSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-project_id")
    serializer_class = ProjectSerializer


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer
