import os
import boto3
import logging
import uuid
from config import Config
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)

s3 = boto3.client("s3")
BUCKET_NAME = Config.S3_BUCKET_NAME

# map filetypes to folders in S3
FILE_TYPE_MAP = {
    "text-files": ["pdf", "doc", "docx", "txt", "md", "epub", "odf"],
    "images": ["jpg", "jpeg", "png", "gif", "gifv", "bmp", "svg", "ico"],
    "video-files": ["mp4", "mov", "avi", "mkv", "webm"],
    "audio-files": ["mp3", "wav", "aac"],
    "spreadsheet-files": ["xlsx", "csv"],
    "archive-files": ["zip", "rar", "7z", "tar", "gz"],
    "code-files": ["sh", "js", "py", "html", "css", "json", "xml"],
    "presentation-files": ["ppt", "pptx"],
    "app-files": ["apk", "exe", "dll"],
    "disc-files": ["iso"],
    "log-files": ["log"],
    "config-files": ["conf", "ini", "yaml", "yml"]

}

def get_folder(extension):
    """determines file folder based on file extension"""
    for folder, extensions in FILE_TYPE_MAP.items():
        if extension.lower() in extensions:
            return folder
        return "other"

@upload_bp.route("/upload/presigned-url", methods=["POST"])
@cross_origin(
    origins="http://127.127.0.0.1:5000",
    allow_headers=["Content-Type", "Authorization"]
)
def generate_presigned_url():
    """generates a presigned url for file upload to S3"""

    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    file_name = data.get("fileName")
    content_type = data.get("contentType")
    file_size = data.get("fileSize")

    if not file_name or not content_type or file_size is None:
        return jsonify({
            "error": "Invalid request"
        }), 400
    
    # check if file size exceeds the 2.5GB limit
    max_size = 2.5 * 1024 * 1024 * 1024
    if file_size > max_size:
        return jsonify({
            "error": "File size exceeds the max limit"
        }), 400
    
    try:
        file_extension = os.path.splitext(file_name)[1][1:]
        folder = get_folder(file_extension)
        secure_name = secure_filename(file_name)

        file_key = f"{folder}/{uuid.uuid4()}-{secure_name}"

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
