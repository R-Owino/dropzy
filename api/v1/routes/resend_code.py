from flask import (Blueprint,
                   jsonify,
                   session)
from v1.cognito import resend_verification_code

# Define Blueprint for resending verification code route
resend_bp = Blueprint("resend", __name__)


@resend_bp.route("/resend_verification", methods=["POST"])
def resend_verification():
    """
    Handle resending verification code to the user's email

    POST:
        - Retrieve the email from session
        - If no email is found, return a 400 error
        - Call Amazon Cognito to resend the verification code
        - If successful, return a success message
        - If unsuccessful, return an error message

    Returns:
        JSON response:
            - 400 Bad Request: no email found in session
            - 200 OK: verification code resent successfully
            - 500 Internal Server Error: Cognito returns an error
    """

    email = session.get("verification_email")

    if not email:
        return jsonify(
            {"success": False, "message": "No email to verify."}
        ), 400

    result = resend_verification_code(email)

    if result["Success"]:
        return jsonify(
            {"success": True, "message": "Verfication code resent."}
        ), 200
    else:
        return jsonify(
            {"success": False, "message": result["message"]}
        ), 500
