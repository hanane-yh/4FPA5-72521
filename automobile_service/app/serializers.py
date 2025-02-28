from rest_framework import serializers
from .models import Automobile, Part, PartFile


class PartFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = PartFile
        fields = ['id', 'file']

    def get_file(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class PartSerializer(serializers.ModelSerializer):
    files = PartFileSerializer(many=True, read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'name', 'files']


class AutomobileSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)

    class Meta:
        model = Automobile
        fields = ['id', 'manufacturer', 'type', 'model', 'parts']


class UploadFileContentSerializer(serializers.Serializer):
    file_name = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
