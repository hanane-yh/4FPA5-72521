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
    def get(self, request, automobile_id):
        automobile = get_object_or_404(Automobile, id=automobile_id)
        parts = automobile.parts.all()
        serializer = PartSerializer(parts, many=True, context={'request': request})
        return Response(serializer.data)


class UploadFileView(APIView):
    def get(self, request, automobile_id, part_id):
        serializer = UploadFileContentSerializer(data={"file_name": "", "content": ""})
        return Response(serializer.initial_data)

    def post(self, request, automobile_id, part_id):
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
    def get(self, request, part_id, file_id):
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
    def get(self, request, part_id):
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
    def get(self, request, automobile_id):
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
    def get(self, request):
        queryset = Automobile.objects.all()
        serializer = AutomobileSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class GetAutomobileView(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(Automobile, pk=pk)
        serializer = AutomobileSerializer(queryset, many=False)
        return Response(serializer.data)
