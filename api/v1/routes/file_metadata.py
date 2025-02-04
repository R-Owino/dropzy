import requests
from . import file_metadata_bp
from config import Config
from flask import jsonify, session

AWS_API_GATEWAY_FETCH_METADATA_URL = Config.AWS_API_GATEWAY_FETCH_METADATA_URL


@file_metadata_bp.route("/file-metadata", methods=["GET"])
def file_metadata():
    """
    Fetch recent file metadata from documents DynamoDB table
    via API gateway with optional limit
    """
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        headers = {"Authorization": f"Bearer {session.get('id_token')}"}
        params = {"limit": 15}
        response = requests.get(
            AWS_API_GATEWAY_FETCH_METADATA_URL,
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": f"Failed to fetch files: {response.text}"
            }), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
