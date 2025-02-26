import os
import boto3
import logging
from . import upload_bp
import v1.config
from flask_cors import cross_origin
from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from botocore.client import Config
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


@upload_bp.route("/upload/initialize", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"])
def initialize_multipart_upload():
    """
    Initializes multipart upload session to S3

    POST:
        - Requires user authentication
        - Requires JSON payload with:
            - `fileName` (str): Name of the file to be uploaded
            - `contentTYpe` (str): MIME type of the file
        - Validates file name and type
        - Calls S3 to create a multipart upload session

    Returns:
        JSON Response:
            - 401 Unauthorized: User not logged in
            - 400 Bad Request: Missing or invalid parameters
            - 415 Unsupported Media Type: Content-Type must be
                application/json
            - 200 OK: Multipart upload initialized successfully
            - 500 Internal Server Error: AWS Credentials issue
                or other failures
    """
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_name = data.get("fileName")
    content_type = data.get("contentType")

    if not file_name or not content_type:
        return jsonify({
            "error": "Invalid request"
        }), 400

    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 415

    # validate filename
    if ".." in file_name or file_name.startswith("/"):
        return jsonify({
            "error": "Invalid filename"
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
        s3 = boto3.client(
            "s3",
            config=Config(s3={'use_accelerate_endpoint': True})
        )

        folder = get_folder(file_extension)
        file_key = f"{folder}/{secure_filename(file_name)}"

        response = s3.create_multipart_upload(
            Bucket=v1.config.Config.S3_BUCKET_NAME,
            Key=file_key,
            ContentType=content_type
        )

        return jsonify({
            "uploadId": response["UploadId"],
            "key": file_key
        })
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"Error initializing multipart upload: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@upload_bp.route("/upload/chunk-url", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"])
def get_chunk_upload_url():
    """
    Generates a pre-signed URL for uploading a specific chunk of a file to S3

    POST:
        - Requires user authentication
        - Requires JSON payload with:
            - `fileName` (str): Name of the file being uploaded
            - `uploadId` (str): ID of the multipart upload session
            - `partNumber` (int): The part number (1-based index)
                of the file chunk
        - Calls S3 to generate a pre-signed URL for the chunk upload

    Returns:
        JSON response:
            - 401 Unauthorized: User not logged in
            - 400 Bad Request: Missing or invalid parameters
            - 200 OK: Chunk upload URL generated successfully
            - 500 Internal Server Error: AWS errors or other failures
    """
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_name = data.get("fileName")
    upload_id = data.get("uploadId")
    part_number = data.get("partNumber")

    try:
        part_number = int(part_number)
        if part_number < 1:
            return jsonify({"error": "Invalid part number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid part number"}), 400

    if not all([file_name, upload_id]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        s3 = boto3.client("s3")
        folder = get_folder(os.path.splitext(file_name)[1][1:])
        file_key = f"{folder}/{secure_filename(file_name)}"

        url = s3.generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": v1.config.Config.S3_BUCKET_NAME,
                "Key": file_key,
                "UploadId": upload_id,
                "PartNumber": part_number
            },
            ExpiresIn=3600
        )

        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@upload_bp.route("/upload/complete", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"])
def complete_multipart_upload():
    """
    Completes a multipart upload session in S3

    POST:
        - Requires user authentication
        - Requires JSON payload with:
            - `key` (str): The file key in S3
            - `uploadId` (str): The multipart upload ID
            - `parts` (list): List of uploaded file parts with ETags
        - Calls S3 to finalize the multipart upload

    Returns:
        JSON response:
            - 401 Unauthorized: User not logged in
            - 400 Bad Request: Missing or invalid parameters
            - 200 OK: Upload completed successfully
            - 500 Internal Server Error: AWS errors or other failures
    """
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_key = data.get("key")
    upload_id = data.get("uploadId")
    parts = data.get("parts")

    try:
        s3 = boto3.client("s3")
        s3.complete_multipart_upload(
            Bucket=v1.config.Config.S3_BUCKET_NAME,
            Key=file_key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts}
        )

        return jsonify({"message": "Upload completed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
