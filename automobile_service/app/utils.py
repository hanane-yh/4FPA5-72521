import io
import zipfile
import os
from typing import List, Any, Dict
from rest_framework.request import Request
from .models import Part, PartFile


def create_zip(file_paths: List[str]) -> io.BytesIO:
    """
    Creates an in-memory ZIP file from the given file paths.

    :param file_paths: A list of file paths to include in the ZIP archive.
    :return: A BytesIO object containing the ZIP data in memory.
    """
    in_memory = io.BytesIO()
    with zipfile.ZipFile(in_memory, 'w') as zf:
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            zf.write(file_path, arcname=filename)
    in_memory.seek(0)
    return in_memory


def build_payload(request: Request, part: Part, part_file: PartFile) -> Dict[str, Any]:
    """
    Builds a minimal JSON payload containing automobile info,
    part info, and a link to the uploaded file.

    :param request: The incoming HTTP request, used to build absolute URLs.
    :param part: The Part instance associated with the file.
    :param part_file: The PartFile instance representing the uploaded file.
    :return: A dictionary with 'automobile' and 'part' keys describing the resource.
    """
    automobile = part.automobile
    file_download_link = request.build_absolute_uri(part_file.file.url)

    payload = {
        "automobile": {
            "manufacturer": automobile.manufacturer,
            "model": automobile.model,
            "type": automobile.type,
        },
        "part": {
            "name": part.name,
            "file_link": file_download_link
        }
    }
    return payload
