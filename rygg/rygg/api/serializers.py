from rygg.api.models import Project, Model, Notebook, FileLink, Dataset
from rest_framework import serializers


class NotebookSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.available_objects.all())
    location = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = ["notebook_id",
                  "project",
                  "name",
                  "created",
                  "updated",
                  "location"]

    def create(self, validated_data):

        request = self.context.get('request', {})
        location = request.data.get('location', '')

        filelink = FileLink.objects.create(resource_locator=location)
        filelink.save()

        notebook = Notebook.available_objects.create(**validated_data)
        notebook.filelink = filelink
        notebook.save()

        return notebook

    def update(self, instance, validated_data):

        request = self.context.get('request', {})
        location = request.data.get('location', '')

        filelink = instance.filelink

        if filelink.resource_locator != location:
            filelink.resource_locator = location
            filelink.save()

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def get_location(self, obj):
        return obj.filelink.resource_locator



class ProjectSerializer(serializers.ModelSerializer):
    models = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    notebooks = NotebookSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = ["project_id",
                  "name",
                  "default_directory",
                  "created",
                  "updated",
                  "is_removed",
                  "models",
                  "notebooks"]

class DatasetSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.available_objects.all())
    models = serializers.PrimaryKeyRelatedField(queryset=Model.available_objects.all(), required=False, many=True)

    class Meta:
        model = Dataset
        fields = ["dataset_id",
                  "project",
                  "name",
                  "created",
                  "modified",
                  "is_removed",
                  "location",
                  "status",
                  "models",
                  ]

class ModelSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.available_objects.all())
    datasets = serializers.PrimaryKeyRelatedField(queryset=Dataset.available_objects.all(), required=False, many=True)

    class Meta:
        model = Model
        fields = ["model_id",
                  "project",
                  "name",
                  "created",
                  "updated",
                  "is_removed",
                  "saved_by",
                  "location",
                  "saved_version_location",
                  "datasets",
                  ]

