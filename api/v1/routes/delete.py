import requests
from v1.config import Config
import logging
from flask import Blueprint, request, jsonify, session

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define Blueprint for delete routes
delete_bp = Blueprint("delete", __name__)

AWS_API_GATEWAY_DELETE_URL = Config.AWS_API_GATEWAY_DELETE_URL


@delete_bp.route("/delete", methods=["DELETE"])
def delete_file():
    """
    Handle file deletion request

    DELETE:
        - Requires user authentication
        - Requires a `file_key` query parameter specifying the file to delete
        - Calls Amazon API Gateway to delete the specified file
        - Handles network errors and API failures gracefully

    Returns:
        JSON response:
            - 401 Unauthorized: user not logged in
            - 400 Bad Request: `file_key` missing
            - 200 OK: file deleted successfully
            - 500 Internal Server Error: API or network failures
    """
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    file_key = request.args.get("file_key")
    logger.info(f"Received file_key: {file_key}")

    if not file_key:
        return jsonify({
            "error": "Missing file_key parameter"
        }), 400
    
    if ".." in file_key or file_key.startswith("/"):
        return jsonify({
            "error": "Invalid file key"
        }), 400

    try:
        id_token = session.get("id_token")
        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.delete(
            AWS_API_GATEWAY_DELETE_URL,
            headers=headers,
            params={"file_key": file_key}
        )

        return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return jsonify({
            "error": f"Network error: {str(e)}"
        }), 500
