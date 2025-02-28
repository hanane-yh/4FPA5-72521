import io
import zipfile
import os


def create_zip(file_paths):
    in_memory = io.BytesIO()
    with zipfile.ZipFile(in_memory, 'w') as zf:
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            zf.write(file_path, arcname=filename)
    in_memory.seek(0)
    return in_memory


def build_payload(request, part, part_file):
    """
    Builds a minimal JSON payload containing automobile info,
    part info, and a link to the uploaded file.
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
