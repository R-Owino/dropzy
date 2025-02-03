import requests
from . import file_metadata_bp
from config import Config
from flask import jsonify, session, request

AWS_API_GATEWAY_FETCH_METADATA_URL = Config.AWS_API_GATEWAY_FETCH_METADATA_URL

@file_metadata_bp.route("/search-files", methods=["GET"])
def search_files():
    """
    search files by name
    """
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    search_term = request.args.get('search', '')
    if not search_term:
        return jsonify({
            "error": "Search term is required"
        }), 400

    try:
        headers = {"Authorization": f"Bearer {session.get('id_token')}"}
        params = {"search": search_term}
        response = requests.get(
            AWS_API_GATEWAY_FETCH_METADATA_URL,
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": f"failed to search files: {response.text}"
            }), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
