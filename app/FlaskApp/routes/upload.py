import base64
import requests
import logging
from config import Config
from flask import Blueprint, request, jsonify, session

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)

AWS_API_GATEWAY_UPLOAD_URL = Config.AWS_API_GATEWAY_UPLOAD_URL

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    """handles file upload to s3 bucket"""

    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]

    # read the file content
    file_content = file.read()

    # validate file size
    MAX_SIZE = 2.5 * 1024 * 1024 * 1024
    if len(file_content) > MAX_SIZE:
        return jsonify({
            "error": f"{file.filename} exceeds the maximum size"}), 400
    
    # encode the file content
    file_base64 = base64.b64encode(file_content).decode("utf-8")

    # prepare payload for API Gateway
    payload = {
        "file_content": file_base64,
        "file_name": file.filename,
        "content_type": file.content_type
        }

    # forward request to API gateway
    id_token = session.get("id_token")
    try:
        if not id_token:
            return jsonify({
                "error": "no ID token found"
            }), 401
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        logger.info(f"Request headers: {headers}")

        response = requests.post(
            AWS_API_GATEWAY_UPLOAD_URL,
            json=payload,
            headers=headers,
            timeout=(3.05, 300)
        )

        logger.info(
            f"API Gateway response: {response.status_code} {response.text}"
        )

        response.raise_for_status()
        return jsonify(response.json())
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Failed to upload {file.filename}: {str(e)}"
        }), 500
