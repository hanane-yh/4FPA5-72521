from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Automobile, Part, PartFile
from .serializers import PartSerializer, UploadFileContentSerializer, AutomobileSerializer
from automobile_service.celery import app as celery_app
from app.models import Automobile
import os
from .utils import create_zip, build_payload


class ListPartsView(APIView):
    """
    Retrieves a list of parts for a specific automobile.
    """

    def get(self, request, automobile_id):
        """
        Handles GET requests to list all parts associated with a given automobile.

        :param request: The incoming HTTP request.
        :param automobile_id: The ID of the automobile to retrieve parts for.
        :return: A Response containing serialized parts data.
        """

        automobile = get_object_or_404(Automobile, id=automobile_id)
        parts = automobile.parts.all()
        serializer = PartSerializer(parts, many=True, context={'request': request})
        return Response(serializer.data)


class UploadFileView(APIView):
    def get(self, request, automobile_id, part_id):
        """
        Returns an initial serializer structure for uploading file content.

        :param request: The incoming HTTP request.
        :param automobile_id: The ID of the automobile.
        :param part_id: The ID of the part to which the file will be uploaded.
        :return: A Response with an initial data structure for file upload.
        """

        serializer = UploadFileContentSerializer(data={"file_name": "", "content": ""})
        return Response(serializer.initial_data)

    def post(self, request, automobile_id, part_id):
        """
        Handles the POST request to upload a file for a specified part,
        creates a PartFile object, and triggers an email task via Celery.

        :param request: The incoming HTTP request containing file_name and content.
        :param automobile_id: The ID of the automobile.
        :param part_id: The ID of the part to which the file is being uploaded.
        :return: A Response indicating success or any validation errors.
        """

        part = get_object_or_404(Part, id=part_id, automobile__id=automobile_id)

        serializer = UploadFileContentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_name = serializer.validated_data['file_name']
        content = serializer.validated_data['content']

        file_bytes = content.encode('utf-8')
        file_obj = SimpleUploadedFile(file_name, file_bytes)
        part_file = PartFile.objects.create(part=part, file=file_obj)

        payload = build_payload(request, part, part_file)

        celery_app.send_task('email_app.tasks.send_email_task', args=[payload])

        return Response(
            {"message": "File uploaded successfully.", "file_id": part_file.id},
            status=status.HTTP_201_CREATED)


class DownloadSingleFileView(APIView):
    """
    Downloads a single file for a given part and file ID.
    """

    def get(self, request, part_id, file_id):
        """
        Returns a downloadable file response for the specified part file.

        :param request: The incoming HTTP request.
        :param part_id: The ID of the part.
        :param file_id: The ID of the file to download.
        :return: An HttpResponse prompting the user to download the file.
        """

        part = get_object_or_404(Part, id=part_id)
        part_file = get_object_or_404(PartFile, id=file_id, part=part)
        file_path = part_file.file.path

        with open(file_path, 'rb') as f:
            file_data = f.read()

        filename = os.path.basename(file_path)

        response = HttpResponse(file_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


class DownloadAllFilesForPartView(APIView):
    """
    Downloads all files for a specific part as a single ZIP archive.
    """

    def get(self, request, part_id):
        """
        Creates a ZIP archive of all files for the given part and returns it
        as a downloadable response.

        :param request: The incoming HTTP request.
        :param part_id: The ID of the part.
        :return: An HttpResponse with a ZIP file attachment.
        """

        part = get_object_or_404(Part, id=part_id)
        files = part.files.all()
        if not files:
            return Response({"error": "No files found for this part."}, status=status.HTTP_404_NOT_FOUND)
        file_paths = [pf.file.path for pf in files]
        zip_file = create_zip(file_paths)
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{part.name}_{part.automobile}_files.zip"'
        return response


class DownloadAllFilesForAutomobileView(APIView):
    """
    Downloads all files for a specific automobile as a single ZIP archive.
    """

    def get(self, request, automobile_id):
        """
        Creates a ZIP archive of all files associated with the given automobile
        and returns it as a downloadable response.

        :param request: The incoming HTTP request.
        :param automobile_id: The ID of the automobile.
        :return: An HttpResponse with a ZIP file attachment.
        """

        automobile = get_object_or_404(Automobile, id=automobile_id)
        parts = automobile.parts.all()
        file_paths = []
        for part in parts:
            for pf in part.files.all():
                file_paths.append(pf.file.path)
        if not file_paths:
            return Response({"error": "No files found for this automobile."}, status=status.HTTP_404_NOT_FOUND)
        zip_file = create_zip(file_paths)
        response = HttpResponse(zip_file, content_type='application/zip')
        response[
            'Content-Disposition'] = f'attachment; filename="{automobile.manufacturer}_{automobile.model}_files.zip"'
        return response


class ListAutomobilesView(APIView):
    """
    Lists all automobiles in the system.
    """

    def get(self, request):
        """
        Retrieves a list of all Automobile instances and returns them in serialized form.

        :param request: The incoming HTTP request.
        :return: A Response containing serialized Automobile data.
        """

        queryset = Automobile.objects.all()
        serializer = AutomobileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class GetAutomobileView(APIView):
    """
    Retrieves a single Automobile by its primary key.
    """

    def get(self, request, pk):
        """
        Returns the details of a specific Automobile identified by 'pk'.

        :param request: The incoming HTTP request.
        :param pk: The primary key of the Automobile to retrieve.
        :return: A Response with the serialized Automobile data.
        """

        queryset = get_object_or_404(Automobile, pk=pk)
        serializer = AutomobileSerializer(queryset, many=False)
        return Response(serializer.data)
