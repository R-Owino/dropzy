import base64
import requests
from config import Config
from flask import Blueprint, request, jsonify, session

upload_bp = Blueprint("upload", __name__)

API_GATEWAY_URL = Config.API_GATEWAY_URL

@upload_bp.route("/upload", method=["POST"])
def upload_file():
    """handles file upload to s3 bucket"""
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    uploaded_files = request.files.getlist("file")
    response_data = []

    for file in uploaded_files:
        # validate file size
        MAX_SIZE = 2.5 * 1024 * 1024 * 1024
        if file.content_length > MAX_SIZE:
            return jsonify({
                "error": f"{file.filename} exceeds the maximum size"}), 400
        
        # read the file
        file_content = file.read()
        file_base64 = base64.b64encode(file_content).decode("utf-8")

        # prepare payload for API Gateway
        payload = {
            "file_content": file_base64,
            "file_name": file.filename,
            "content_type": file.content_type
        }

        # forward request to API gateway
        headers = {"Authorization": f"Bearer {session.get('access_token')}"}
        response = requests.post(API_GATEWAY_URL, json=payload, headers=headers)

        if response.status_code == 200:
            response_data.append(response.json())
        else:
            response_data.append({
                "error": f"Failed to upload {file.filename}: {response.text}"})

    return jsonify(response_data)
