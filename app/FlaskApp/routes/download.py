from flask import Blueprint, request, jsonify, session, redirect
import requests
from config import Config

download_bp = Blueprint("download", __name__)

API_GATEWAY_URL = Config.API_GATEWAY_URL

@download_bp.route("/download", methods=["GET"])
def download_file():
    """
    Requests a pre-signed URL for downloading a file from S3
    Passes thru file_key directly to the lambda function
    """
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # prepare headers with auth
        headers = {"Authorization": f"Bearer {session.get.access_token}"}

        # forward the query string to the download lambda function
        response = requests.get(
            API_GATEWAY_URL,
            headers=headers,
            params=request.args
        )

        if response.status_code == 200:
            presigned_url = response.json().get("presigned_url")
            if presigned_url:
                return redirect(presigned_url)
            else:
                return jsonify({"error": "No pre-signed URL generated"}), 500
        else:
            return jsonify({
                "error": f"Failed to generate download URL: {response.text}"
            }), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
