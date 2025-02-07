import requests
from . import file_metadata_bp
from v1.config import Config
from flask import jsonify, session, request

AWS_API_GATEWAY_FETCH_METADATA_URL = Config.AWS_API_GATEWAY_FETCH_METADATA_URL


@file_metadata_bp.route("/search-files", methods=["GET"])
def search_files():
    """
    search for files by name

    GET:
        - Requires a user to be logged in
        - Requires a 'search' query parameter
        - Calls Amazon API Gateway to fetch matching file metadata
        - Handles network errors and API failures gracefully

    Returns:
        JSON response:
            - 401 Unauthorized: user not logged in
            - 400 Bad Request: search term is missing
            - 200 OK: search results successful
            - 500 Internal Server Error: API or network failures
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
