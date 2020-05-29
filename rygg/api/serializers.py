from rygg.api.models import Project, Model
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    models = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Project
        fields = ["project_id", "name", "default_directory", "created", "updated", "models"]

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Model
        fields = ["model_id", "project", "name", "created", "updated", "saved_by", "location", "saved_version_location"]
