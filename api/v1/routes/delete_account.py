from flask import session, Blueprint, jsonify, request, redirect, url_for
from v1.cognito import delete_user
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


delete_account_bp = Blueprint("delete-account", __name__)


@delete_account_bp.route("/delete-account", methods=["POST"])
def delete_account():
    """
    Handle user account deletion

    POST:
        - Retrieve user's access_token from session
        - Call Cognito to delete user from Cognito userpool and DynamoDB
        - If successful:
            - Return a 200 JSON response if request
                header `Accept: application/json`is set
            - Otherwise, redirect to the registration page
        - If failed, return a 400 JSON reponse with an error message

    Returns:
        JSON response or redirect:
            - 302 Redirect: login page if unauthorized or
                registration page if successful
            - 200 OK: sucessful deletion
            - 400 Bad Request: deletion fails
            - 500 Internal Server Error: Cognito/DynamoDB errors
                or other failures
    """

    try:
        access_token = session.get("access_token")
        if not access_token:
            if request.headers.get("Accept") == "application/json":
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("api.login.login"))

        result = delete_user(access_token)

        if result["Success"]:
            if request.headers.get("Accept") == "application/json":
                return jsonify({
                    "message": "Account deleted successfully."
                }), 200
            return redirect(url_for("api.register.register"))

        return jsonify({"message": result["message"]}), 400

    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        return jsonify({"message": "Failed to delete account."}), 500
