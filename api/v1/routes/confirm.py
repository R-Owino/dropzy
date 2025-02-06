from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session,
                   jsonify)
from v1.cognito import confirm_user
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define Blueprint for confirmation routes
confirm_bp = Blueprint("confirm", __name__)


@confirm_bp.route("/confirm", methods=["GET", "POST"])
def confirm():
    """
    Handle user email verification via a confirmation code

    GET:
        - If 'verification_email' is missing from session,
            redirect to register page
        - Otherwise, render the confirmation template

    POST:
        - Retrieve verification code from form input
        - Call Amazon Cognito to confirm the user's email
        - If successful or already confirmed, redirect to login page
        - If request header `Accept: application/json`, return a
            JSON response instead of redirecting
        - If failed, return an error message in JSON format
            or re-render the confirmation page

    Returns:
        JSON response:
            - 302 Redirect: login page upon successful verification
            - 200 OK: JSON response if `Accept: application/json` is set
            - 200 OK: rendered confirmation page on failure
    """

    email = session.get("verification_email")
    if not email:
        return redirect(url_for("register.register"))

    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            return render_template("confirm.html")

        code = code.replace(" ", "")

        result = confirm_user(email, code)
        if result.get("Success") or "CONFIRMED" in result.get("message", ""):
            logger.info(
                f"User {email} verified successfully or already confirmed"
            )
            session.pop("verification_email", None)

            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    "success": result.get("Success", True),
                    "redirect_url": url_for("login.login")
                })
            else:
                return redirect(url_for("login.login"))
        else:
            logger.warning(
                f"Verification failed for {email}: {result.get('message')}"
            )
            return jsonify({
                "success": False,
                "message": result.get("message")
            })

    return render_template("confirm.html")
