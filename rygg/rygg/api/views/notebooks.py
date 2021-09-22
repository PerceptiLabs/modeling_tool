from rest_framework import viewsets
from rygg.api.models import Notebook
from rygg.api.serializers import NotebookSerializer

class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.available_objects.filter(project__is_removed=False).order_by("-notebook_id")
    serializer_class = NotebookSerializer
