import requests
from config import Config
from flask import Blueprint, request, jsonify, session

delete_bp = Blueprint("delete", __name__)

AWS_API_GATEWAY_DELETE_URL = Config.AWS_API_GATEWAY_DELETE_URL

@delete_bp.route("/delete", methods=["DELETE"])
def delete_file():
    """
    handles deleting of a file
    """
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    file_key = request.args.get("file_key")
    if not file_key:
        return jsonify({"error": "Missing file_key parameter"}), 400
    
    try:
        headers = {"Authorization": f"Bearer {session.get.access_token}"}
        response = requests.delete(
            AWS_API_GATEWAY_DELETE_URL,
            headers=headers,
            params={"file_key": file_key}
        )

        return jsonify(response.json()), response.status_code
    
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
