import os
import boto3
import logging
from . import upload_bp
from v1.config import Config
from flask_cors import cross_origin
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# map filetypes to folders in S3
FILE_TYPE_MAP = {
    "text-files": ["pdf", "doc", "docx", "txt", "md", "epub", "odt"],
    "image-files": ["jpg", "jpeg", "png", "gif", "gifv", "bmp", "svg", "ico"],
    "video-files": ["mp4", "mov", "avi", "mkv", "webm"],
    "audio-files": ["mp3", "wav", "aac"],
    "spreadsheet-files": ["xlsx", "csv"],
    "archive-files": ["zip", "rar", "7z", "tar", "gz"],
    "code-files": ["sh", "js", "py", "html", "css", "json", "xml", "tf"],
    "presentation-files": ["ppt", "pptx"],
    "app-files": ["apk", "exe", "dll"],
    "disc-files": ["iso"],
    "log-files": ["log"],
    "config-files": ["conf", "ini", "yaml", "yml"],
    "other": []
}


def get_folder(extension: str) -> str:
    """
    Determines the appropriate folder for a file based on its extension

    Args:
        extension (str): the file extension

    Returns:
        str: the folder name where the file should be stored
    """
    for folder, extensions in FILE_TYPE_MAP.items():
        if extension.lower() in extensions:
            return folder
    return "other"


@upload_bp.route("/upload/presigned-url", methods=["POST"])
@cross_origin(
    origins="*",
    allow_headers=["Content-Type", "Authorization"]
)
def generate_presigned_url():
    """
    Generate a pre-signed URL for secure file upload to S3

    POST:
        - Requires user authentication
        - Requires JSON body containing `fileName`, `contentType`
            and `fileSize`
        - Validates file size against a max limit of 2.5GB
        - Generates a pre-signed URL for uploading the file directly to S3

    Returns:
        JSON response:
            - 401 Unauthorized: user not logged in
            - 400 Bad Request: required fields are missing or
                file size exceeds the limit
            - 200 OK: pre-signed URL and file key if successful
            - 500 Internal Server Error: AWS credentials error or
                other failures
    """

    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_name = data.get("fileName")
    content_type = data.get("contentType")
    file_size = data.get("fileSize")

    if not file_name or not content_type or file_size is None:
        return jsonify({
            "error": "Invalid request"
        }), 400

    # validate filename
    if ".." in file_name or file_name.startswith("/"):
        return jsonify({
            "error": "Invalid filename"
        }), 400

    # check if file size exceeds the 2.5GB limit
    max_size = 2.5 * 1024 * 1024 * 1024
    if file_size > max_size:
        return jsonify({
            "error": "File size exceeds the max limit"
        }), 400

    # validate file type
    file_extension = os.path.splitext(file_name)[1][1:].lower()
    if file_extension not in [
        ext for exts in FILE_TYPE_MAP.values() for ext in exts
    ]:
        return jsonify({
            "error": "Unsupported file type"
        }), 400

    try:
        s3 = boto3.client("s3")
        BUCKET_NAME = Config.S3_BUCKET_NAME

        folder = get_folder(file_extension)
        secure_name = secure_filename(file_name)
        file_key = f"{folder}/{secure_name}"

        # generate pre-signed URL for PUT
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": file_key,
                "ContentType": content_type
            },
            ExpiresIn=3600
        )
        return jsonify({
            "url": presigned_url,
            "key": file_key
        })
    except (NoCredentialsError, PartialCredentialsError) as e:
        return jsonify({
            "error": str(e)
        }), 500
