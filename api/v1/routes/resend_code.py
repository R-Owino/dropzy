from flask import (Blueprint,
                   jsonify,
                   session)
from cognito import resend_verification_code

resend_bp = Blueprint("resend", __name__)


@resend_bp.route("/resend_verification", methods=["POST"])
def resend_verification():
    """defines the route for resending the verification code"""

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
