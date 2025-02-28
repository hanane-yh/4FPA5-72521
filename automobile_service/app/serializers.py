from rest_framework import serializers
from .models import Automobile, Part, PartFile


class PartFileSerializer(serializers.ModelSerializer):
    """
    Serializer for the PartFile model that returns a URL for the 'file' field.
    """

    file = serializers.SerializerMethodField()

    class Meta:
        model = PartFile
        fields = ['id', 'file']

    def get_file(self, obj: PartFile) -> str:
        """
        Returns a file URL if the request context is available,
        otherwise returns the relative file path.

        :param obj: The PartFile instance to retrieve the file URL from.
        :return: A string representing the file URL.
        """
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class PartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Part model, including a nested list of associated PartFiles.
    """

    files = PartFileSerializer(many=True, read_only=True)

    class Meta:
        model = Part
        fields = ['id', 'name', 'files']


class AutomobileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Automobile model, including a nested list of associated Parts.
    """

    parts = PartSerializer(many=True, read_only=True)

    class Meta:
        model = Automobile
        fields = ['id', 'manufacturer', 'type', 'model', 'parts']


class UploadFileContentSerializer(serializers.Serializer):
    """
    A serializer that expects two required fields for uploading file content:
     - file_name: The name of the file.
     - content: The plain text content of the file.
    """
    file_name = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
